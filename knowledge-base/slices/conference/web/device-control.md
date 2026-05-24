---
id: conference/device-control
platform: web
api_docs:
  - title: 设备及网络
    url: https://cloud.tencent.com/document/product/647/126923
---

# 设备控制 — Web 实现

## 前置条件
**通用依赖**：见 [login-auth 平台 slice](../login-auth.md)。

**额外依赖**：
- 已安装 `tuikit-atomicx-vue3@latest`

**前置状态**：
- 已阅读 `conference/device-control`，明确当前能力的产品边界。
- 已完成 `conference/login-auth`，确保当前页面具备稳定登录态。
- 已根据业务流程接入会议上下文；需要房间状态时，优先通过 `conference/room-lifecycle` 统一承接。
- 当前能力涉及媒体采集、渲染或浏览器权限时，请在 `HTTPS` 或 `localhost` 安全上下文下调试。

## 最佳实践
### 会议中的麦克风控制推荐采用“进房后预静音 + 建立采集”
- 用户成功进入房间后，先调用 `muteMicrophone()`，先把本地音频上行状态收口为静音。
- 随后调用 `openLocalMicrophone()` 建立本地麦克风采集，保持本地已采集但默认不向远端发送音频。
- 用户点击“打开麦克风”时，调用 `unmuteMicrophone()` 恢复音频上行。
- 用户点击“关闭麦克风”时，调用 `muteMicrophone()` 停止音频上行。
- 只有在离房、结束会议或明确要释放设备时，再调用 `closeLocalMicrophone()`。

这里要特别区分：**麦克风需要把“是否采集”和“是否上行”拆开处理，但摄像头通常不需要照搬这套模型。**
- 摄像头在大多数会议产品里，直接用 `openLocalCamera()` / `closeLocalCamera()` 控制开启与关闭即可。
- 如果业务要求“入会默认不开摄”，应明确调用 `closeLocalCamera()` 收口摄像头关闭状态；当用户点击开摄时再调用 `openLocalCamera()`。
- 如果用户点击关摄，直接调用 `closeLocalCamera()` 释放本地摄像头采集即可，不需要类比成 `muteMicrophone()` / `unmuteMicrophone()` 这类“保留采集但停止上行”的用法。
- 只有在客户明确要求“摄像头预热但默认不展示 / 不上屏”这类特殊策略时，才需要单独评估是否做更复杂的摄像头状态编排；默认文档口径不要把摄像头推断成和麦克风同一套控制链路。

这样设计有两个直接收益：
- 用户开麦时无需重新处理物理设备采集，响应速度更快。
- 业务层可以持续结合 `currentMicVolume` 检测闭麦说话，并在合适时提示“您正在说话，是否打开麦克风？”。

## 代码示例
### 基础接入：打开摄像头、切换设备并在离场前关闭

```ts
import { useDeviceState, DeviceStatus } from 'tuikit-atomicx-vue3/room';

const {
  cameraStatus,
  openLocalCamera,
  closeLocalCamera,
  getCameraList,
  setCurrentCamera,
} = useDeviceState();

if (cameraStatus.value !== DeviceStatus.On) await openLocalCamera();
await getCameraList();
await setCurrentCamera({ deviceId: 'camera_device_id' });
await closeLocalCamera();
```

### 会议推荐：用 `cameraStatus` 驱动摄像头开关按钮

> ⚠️ 重要：`localParticipant.isCameraDisabled` 是管理员/会控禁用状态，**不**反映本地设备的实际开关。会中摄像头开关按钮状态必须来自 `cameraStatus`。

```ts
import { computed } from 'vue';
import { useDeviceState, useRoomParticipantState, DeviceStatus } from 'tuikit-atomicx-vue3/room';

const { cameraStatus, openLocalCamera, closeLocalCamera } = useDeviceState();

// ✅ 正确：用 cameraStatus 反映本地设备实际开关状态
const isCameraOff = computed(() => cameraStatus.value !== DeviceStatus.On);

// ❌ 错误示例（切勿使用）：
// const { localParticipant } = useRoomParticipantState();
// const isCameraOff = computed(() => Boolean(localParticipant.value?.isCameraDisabled));
// → isCameraDisabled 是管理员远程禁用标志，不跟随 openLocalCamera/closeLocalCamera 更新

export async function toggleCamera() {
  if (isCameraOff.value) {
    await openLocalCamera();   // 重新开启摄像头采集
  } else {
    await closeLocalCamera();  // 停止摄像头采集（离场时也应调用）
  }
}
```

### 会议推荐：进房后先静音，再建立麦克风采集

```ts
import { computed } from 'vue';
import { DeviceStatus, useDeviceState, useRoomParticipantState } from 'tuikit-atomicx-vue3/room';

const { microphoneStatus, openLocalMicrophone, currentMicVolume } = useDeviceState();
const { muteMicrophone, unmuteMicrophone } = useRoomParticipantState();

const isMicrophoneOn = computed(() => microphoneStatus.value === DeviceStatus.On);

export async function prepareMicrophoneAfterJoin() {
  await muteMicrophone();
  await openLocalMicrophone();
}

export async function handleClickOpenMicrophone() {
  await unmuteMicrophone();
}

export async function handleClickCloseMicrophone() {
  await muteMicrophone();
}

export function shouldPromptSpeakingWhileMuted() {
  return !isMicrophoneOn.value && currentMicVolume.value > 30;
}
```

## 调用时序
```
完成 login-auth 并进入会议
   │
   ▼
根据页面状态初始化本地设备
   │
   ├─ 摄像头需要开启 → openLocalCamera()
   ├─ 麦克风需要预采集 → muteMicrophone() → openLocalMicrophone()
   ├─ 需切换设备 → getCameraList() / getMicrophoneList() → setCurrent*(...)
   └─ 权限失败 → 展示错误并提示检查浏览器授权
   │
   ▼
用户点击“开麦” → unmuteMicrophone()
   │
   ├─ 检测到闭麦说话 → 可结合 currentMicVolume 给出提醒
   └─ 用户点击“闭麦” → muteMicrophone()
   │
   ▼
离场或明确释放设备时调用 closeLocalCamera() / closeLocalMicrophone()
```

## 平台特有注意事项
### 1. Web 采集设备必须运行在安全上下文
线上环境未启用 `HTTPS` 时，浏览器会直接拦截摄像头和麦克风采集；本地联调可使用 `localhost`。

### 2. 设备切换属于异步动作
切换摄像头、麦克风或扬声器时，建议在 UI 层提供 loading 或“切换中”反馈，避免用户连续点击造成状态错乱。

### 3. 设备错误应直接投射到 UI
摄像头或麦克风异常时，应把 `cameraLastError`、`microphoneLastError` 等状态及时映射成提示，而不是只在控制台打印。

### 4. 工具栏状态应以 AtomicX 状态为准
麦克风按钮应直接用 `useDeviceState().microphoneStatus === DeviceStatus.On` 判断当前是否开麦，再分别调用 `muteMicrophone()` / `unmuteMicrophone()`。自定义工具栏不要额外维护一个容易漂移的本地 `isMuted` 作为唯一事实源；如果业务需要本地 UI 状态，也应从 `microphoneStatus` 派生。

### 5. 设备入口要区分“房间级禁用”和“成员级关闭”
如果当前是 `disableAllDevices` 触发的房间级禁用，这类限制通常只作用于普通成员；普通成员的设备 icon 应表现为 disabled，并在点击时通过 toast 或等价提示说明原因。是否继续允许用户通过 `requestToOpenDevice()` 申请开启，需要结合客户需求决定。若只是被房主或管理员单独关闭设备，则更适合提示“设备已被管理员关闭”，并允许用户在没有房间级禁用的前提下再次调用 `openLocalCamera()` 或 `unmuteMicrophone()` 主动恢复。

### 6. `iframe` 集成要显式放开媒体权限
如果会议页面运行在 `iframe` 内，宿主页面需要通过 `allow` 放开麦克风、摄像头、屏幕共享和全屏权限；否则即使业务代码正确，浏览器也可能直接拦截媒体采集或共享能力。

## 代码生成约束
### 编译必要条件
- **通用条件**：见 [login-auth 平台 slice](../login-auth.md)。
- **额外导入**：至少需要从 `tuikit-atomicx-vue3/room` 导入 `useDeviceState`，按需导入 `DeviceStatus`、`DeviceError`。
- **运行前提**：浏览器具备设备权限，页面处于安全上下文。

### 生成规则
#### MUST（生成时必须包含）

1. **通过 `useDeviceState` 承接本地设备状态与操作** — 这样设备列表、状态与异常才能保持同源。  
   **Verify**: 检查是否存在 `useDeviceState()`。
2. **在切换设备前先获取设备列表或当前状态** — 否则 UI 容易对不存在的设备执行切换。  
   **Verify**: 检查是否存在 `getCameraList()` / `getMicrophoneList()` / 状态读取逻辑。
3. **会议场景下把“麦克风采集”与“音频上行”拆开处理，但不要把这套规则直接套到摄像头上** — 推荐进房后先 `muteMicrophone()`，再 `openLocalMicrophone()`；后续通过 `unmuteMicrophone()` / `muteMicrophone()` 响应开麦与闭麦。摄像头统一按 `openLocalCamera()` / `closeLocalCamera()` 直接控制开关。  
   **Verify**: 检查会议工具栏或入会初始化逻辑中，麦克风是否存在上述调用链，同时摄像头是否统一使用 `openLocalCamera()` / `closeLocalCamera()` 控制。

#### MUST NOT（生成时绝不能出现）

1. **不要在不满足安全上下文时默认开启媒体采集** — 浏览器会直接拒绝访问。  
   **Verify**: 检查代码或说明中是否明确 `HTTPS` / `localhost` 前提。
2. **不要只改 UI 开关，不调用真实设备接口** — 会出现按钮已开但本地流未变化的假状态。  
   **Verify**: 检查交互处理函数中是否实际调用 `open*` / `close*` / `setCurrent*`。
3. **不要把会中的“开麦 / 闭麦”实现成反复 `openLocalMicrophone()` / `closeLocalMicrophone()`** — 这样会增加重新采集延迟，也不利于闭麦说话提醒。  
   **Verify**: 检查工具栏开关逻辑是否优先使用 `muteMicrophone()` / `unmuteMicrophone()`。

### 集成检查点
- 当前 slice 常与 `conference/prejoin-check`、`conference/screen-share`、`conference/beauty-effects` 联动。
- 一般只需要新增设备面板或工具栏逻辑，不应侵入 SDK 内部采集实现。
- 如果业务已存在独立媒体层，需要明确由哪一层负责最终设备开关，避免双写状态。

## 验证矩阵
| 层级 | 检查项 | 验证手段 | 预期结果 |
|------|--------|----------|---------|
| 1. 编译级 | 已导入 `useDeviceState` | 检查 `import` 语句 | 可正常解析设备 Hook |
| 2. 静态规则级 | UI 操作真实调用设备接口 | 搜索 `openLocalCamera` / `openLocalMicrophone` / `muteMicrophone` / `unmuteMicrophone` / `setCurrentCamera` | 至少一条真实设备调用链存在 |
| 3. 运行时级 | 设备开关与切换可执行 | 在浏览器授权后触发操作 | 摄像头状态可切换，麦克风可在静音与上行之间切换 |
| 4. 业务行为级 | 用户能感知权限、切换与闭麦说话提醒 | 在设置面板或工具栏执行操作 | UI 与实际设备状态保持一致，必要时可提示闭麦说话 |
