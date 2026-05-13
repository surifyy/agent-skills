---
id: conference/room-moderation
platform: web
api_docs:
  - title: 房间管理
    url: https://cloud.tencent.com/document/product/647/126919
---

# 会议会控与秩序管理 — Web 实现

## 前置条件
**通用依赖**：见 [login-auth 平台 slice](../login-auth.md)。

**额外依赖**：
- 已安装 `tuikit-atomicx-vue3@latest`

**前置状态**：
- 已阅读 `conference/room-moderation`，明确当前能力的产品边界。
- 已完成 `conference/login-auth`，确保当前页面具备稳定登录态。
- 已根据业务流程接入会议上下文；需要房间状态时，优先通过 `conference/room-lifecycle` 统一承接。

## 最佳实践
### 1. 明确 `disableAllDevices` 的作用范围和成员侧表现
- 房主和管理员都可以调用 `disableAllDevices()`。
- `disableAllDevices()` 可作用于麦克风、摄像头和屏幕分享，通常只限制普通成员；房主和管理员仍应保留对应会控与协作能力。
- 开启全体设备禁止后，普通成员的设备或共享入口应表现为 disabled，同时通过 toast 或等价提示明确告知当前受房间规则限制。
- 用户点击被禁用的入口时，可按客户需求决定是否继续提供“申请开启”动作；如果要做该能力，建议通过 `requestToOpenDevice()` 向房主或管理员发起申请。
- 如果只是被房主或管理员单独关闭摄像头、麦克风或屏幕分享，普通成员也应收到 toast 提示；但这类限制通常不是持续禁用，只要没有叠加房间级禁用，成员仍可再次主动开启对应能力。

### 2. 房主 / 管理员端的会控按钮必须是 toggle，而不是单向动作
- `disableAllDevices()` 与 `disableAllMessages()` 都支持通过 `disable: true / false` 在“开启限制”和“解除限制”之间切换。
- 管理端按钮文案、icon 和二次确认文案应围绕当前状态成对出现，例如“全体静音 / 解除全体静音”、“禁止所有人开启麦克风 / 允许所有人开启麦克风”。
- 如果页面里没有现成的 SDK 响应式字段可直接读取当前房间级会控状态，就应由业务层维护一个房间级会控读模型，再由按钮层消费；不要把状态只放在一次点击的临时 `ref` 里。

### 3. 页面刷新或重进房后，要从房间级状态恢复管理端按钮态
- 本地 `ref` 只适合作为当前页面的 UI cache，不适合作为房间级会控状态的唯一来源。
- 进入会议、管理面板重新挂载或页面刷新后，应从当前房间状态同步结果、房间信息映射结果，或业务后端保存的会控快照中恢复管理端按钮态。
- 如果房间级状态恢复失败，管理端至少应显式退回“未知态 / 加载中”，而不是默认假定所有全体规则都已解除。

### 4. 明确 `disableAllMessages` 的作用范围
房主和管理员都可以调用 `disableAllMessages()`；但该规则更适合作用于普通成员。房主和管理员通常仍应保留必要的管理沟通能力，避免在处理会控时把自己也一并锁死。

## 代码示例
### 管理端会控：toggle 全员规则，并维护可回显的按钮状态

```ts
import { computed, onMounted, onUnmounted, reactive, watch } from 'vue';
import {
  DeviceType,
  RoomParticipantEvent,
  useRoomParticipantState,
  useRoomState,
} from 'tuikit-atomicx-vue3/room';

const { currentRoom } = useRoomState();
const {
  disableAllDevices,
  disableAllMessages,
  closeParticipantDevice,
  subscribeEvent,
  unsubscribeEvent,
} = useRoomParticipantState();

const roomModerationUiState = reactive({
  allMicrophoneDisabled: false,
  allCameraDisabled: false,
  allMessagesDisabled: false,
});

const moderationActionText = computed(() => ({
  microphone: roomModerationUiState.allMicrophoneDisabled ? '解除全体静音' : '全体静音',
  camera: roomModerationUiState.allCameraDisabled ? '解除全体禁画' : '全体禁画',
  message: roomModerationUiState.allMessagesDisabled ? '解除全体禁言' : '全体禁言',
}));

watch(
  () => currentRoom.value?.roomId,
  async (roomId) => {
    if (!roomId) {
      roomModerationUiState.allMicrophoneDisabled = false;
      roomModerationUiState.allCameraDisabled = false;
      roomModerationUiState.allMessagesDisabled = false;
      return;
    }

    await hydrateModerationUiState(roomId);
  },
  { immediate: true },
);

async function hydrateModerationUiState(roomId: string) {
  console.log('进入房间后，从房间级会控状态源恢复按钮态:', roomId);
  // 例如：从当前房间状态同步结果、roomInfo 映射结果，
  // 或业务服务端保存的 moderation snapshot 恢复这三个布尔值。
  // 如果没有这一步，页面刷新后管理端按钮只能退回默认值，
  // 无法正确回显当前房间的全体静音 / 禁画 / 禁言状态。
}

async function toggleAllMicrophoneDisabled() {
  const nextDisabled = !roomModerationUiState.allMicrophoneDisabled;

  try {
    await disableAllDevices({
      deviceType: DeviceType.Microphone,
      disable: nextDisabled,
    });
    roomModerationUiState.allMicrophoneDisabled = nextDisabled;
  } catch (error) {
    console.error('切换全体静音失败', error);
  }
}

async function toggleAllCameraDisabled() {
  const nextDisabled = !roomModerationUiState.allCameraDisabled;

  try {
    await disableAllDevices({
      deviceType: DeviceType.Camera,
      disable: nextDisabled,
    });
    roomModerationUiState.allCameraDisabled = nextDisabled;
  } catch (error) {
    console.error('切换全体禁画失败', error);
  }
}

async function toggleAllMessagesDisabled() {
  const nextDisabled = !roomModerationUiState.allMessagesDisabled;

  try {
    await disableAllMessages({ disable: nextDisabled });
    roomModerationUiState.allMessagesDisabled = nextDisabled;
  } catch (error) {
    console.error('切换全体禁言失败', error);
  }
}

async function closeUserMicrophone(userId: string) {
  try {
    await closeParticipantDevice({
      userId,
      deviceType: DeviceType.Microphone,
    });
  } catch (error) {
    console.error('关闭成员麦克风失败', error);
  }
}

async function closeUserCamera(userId: string) {
  try {
    await closeParticipantDevice({
      userId,
      deviceType: DeviceType.Camera,
    });
  } catch (error) {
    console.error('关闭成员摄像头失败', error);
  }
}

async function closeUserScreenShare(userId: string) {
  try {
    await closeParticipantDevice({
      userId,
      deviceType: DeviceType.ScreenShare,
    });
  } catch (error) {
    console.error('关闭成员屏幕共享失败', error);
  }
}

function onParticipantDeviceClosed({ device, operator }) {
  console.warn('成员设备已被管理员关闭:', device, operator);
}

onMounted(() => {
  subscribeEvent(RoomParticipantEvent.onParticipantDeviceClosed, onParticipantDeviceClosed);
});

onUnmounted(() => {
  unsubscribeEvent(RoomParticipantEvent.onParticipantDeviceClosed, onParticipantDeviceClosed);
});
```

> **说明：**
> - 这段示例故意把 `disable: true` 和 `disable: false` 都走通，模板层可直接消费 `moderationActionText` 生成 toggle 按钮文案。
> - 当前仓库没有证据表明 SDK 一定直接提供了一个就叫 `isAllMicrophoneDisabled` 的现成响应式字段；如果你的项目已经有这类字段，可以直接替换 `roomModerationUiState`，否则应由业务层维护等价读模型。
> - 页面刷新、重进房或管理面板重新挂载后，应重新执行 `hydrateModerationUiState()` 这类恢复逻辑，而不是默认把所有会控按钮重置为未禁用。

### 单成员关闭设备：更适合“纠正当前状态”，不等于持续禁用

`closeParticipantDevice()` 适合在成员已经打开麦克风、摄像头或屏幕共享时，房主或管理员立即把它关掉；它更像一次“纠正当前设备状态”的会控动作，而不是房间级长期限制。

如果业务想表达“普通成员后续也不能再自行打开该设备”，应优先使用 `disableAllDevices()` 做房间级禁用；如果只是单次关闭某个成员设备，则成员端应收到明确提示，并在没有房间级禁用的前提下允许再次主动开启。

## 调用时序
```
完成 login-auth 并进入会议
   │
   ▼
根据本地角色展示房主 / 管理员会控面板
   │
   ├─ 先恢复当前房间级会控状态，生成 toggle 按钮文案与禁用态
   ├─ 全员规则 → disableAllDevices / disableAllMessages（支持 disable: true / false）
   ├─ 单成员控制 → closeParticipantDevice
   └─ 状态变更后 → 管理端与成员端 UI 同步刷新并收口入口
```

## 平台特有注意事项
### 1. 创建期规则与会中会控要分层
默认禁麦、禁聊等会议初始规则属于 `conference/room-config`；会中动态控制才属于当前 slice。

### 2. 被控制方必须得到清晰反馈
远程关闭麦克风、摄像头或禁言后，被控制成员需要在本端看到明确提示，否则很容易误以为是本地故障。

### 3. 管理端按钮状态要和房间级会控保持同源
全员禁言、禁共享或禁设备的结果不应只靠点击瞬间更新一个局部变量；更合理的做法是让房主 / 管理员按钮与房间级会控读模型同源，保证按钮文案、toggle 态和真实规则一致。

### 4. 页面刷新后不要假设管理端会控已自动丢失
如果产品要求房主 / 管理员在刷新后继续看到当前房间仍处于“全体静音 / 禁画 / 禁言”等状态，就必须在重进房后重新拉取或订阅房间级会控状态，并据此恢复按钮态。是否存在现成 SDK 字段取决于实际接入；当前 slice 不应虚构固定字段名。

### 5. 设备与共享入口要同时表达“不可用原因”和“恢复方式”
普通成员遇到 `disableAllDevices()` 触发的房间级禁用时，设备或共享按钮不应只做成不可点击的灰态而没有解释；至少应给出 toast 或等价提示，并根据产品需求决定是否在点击时调用 `requestToOpenDevice()`。这类房间级禁用通常不影响房主和管理员。如果只是被单独关闭设备或共享，则入口不应长期保持 disabled，而应允许成员在没有房间级禁用的前提下再次主动恢复对应能力。

## 代码生成约束
### 编译必要条件
- **通用条件**：见 [login-auth 平台 slice](../login-auth.md)。
- **额外导入**：至少需要导入 `useRoomParticipantState`，按需导入 `DeviceType`。
- **运行前提**：当前用户已在会议内，且具备房主或管理员权限。

### 生成规则
#### MUST（生成时必须包含）

1. **通过 `useRoomParticipantState` 执行会控动作** — 这样成员状态和 UI 感知才可统一收口。  
   **Verify**: 检查是否存在 `disableAllDevices` / `disableAllMessages` / `closeParticipantDevice`。
2. **房主 / 管理员端的房间级会控按钮必须体现当前状态，并支持 toggle 解除** — 不能只展示“全体静音”“全体禁言”这类单向动作。  
   **Verify**: 检查管理端是否根据当前状态生成“开启限制 / 解除限制”两种文案，且 `disable` 参数会在 `true / false` 之间切换。
3. **把会控结果映射到成员端交互状态** — 否则页面会出现“按钮可点但实际被禁用”的错觉。  
   **Verify**: 检查聊天、设备或共享入口是否联动最新状态。
4. **让管理端按钮状态从可恢复的房间级状态源初始化或回填** — 页面刷新、重进房或面板重新挂载后，管理端仍应能回显当前全员规则。  
   **Verify**: 检查是否存在初始化 / 恢复房间级会控状态的逻辑，而不是把按钮态永久写死在页面局部 `ref` 里。
5. **按角色区分全体规则的实际生效范围** — `disableAllDevices` / `disableAllMessages` 的成员侧表现应与房主、管理员、普通成员的权限边界一致。  
   **Verify**: 检查普通成员与房主 / 管理员是否使用了不同的入口态或执行分支。

#### MUST NOT（生成时绝不能出现）

1. **不要把创建期配置当作会中控制复用** — 会造成语义混乱。  
   **Verify**: 检查会控逻辑是否仍与 `room-config` 分层。
2. **不要把房间级会控按钮做成只会下发 `disable: true` 的单向动作** — 真实产品中的全体静音 / 禁画 / 禁言都应支持解除。  
   **Verify**: 检查是否缺少 `disable: false` 的解除路径或等价 toggle 分支。
3. **不要只在管理端成功提示，不处理成员端反馈** — 被控制用户会误判为本地故障。  
   **Verify**: 检查成员端是否有提示或状态联动逻辑。
4. **不要把全体规则状态只存在当前页面内存中** — 页面刷新后如果直接丢失，会导致房主端 UI 与真实房间规则脱节。  
   **Verify**: 检查是否没有任何房间级状态恢复逻辑。
5. **不要在房间级禁用仍生效时让普通成员直接调用开启能力** — 这会绕开会控语义，也会导致“点了没反应”的混乱体验。  
   **Verify**: 检查普通成员在全体禁设备或禁共享时是否优先走提示或申请链路，而不是直接 `open*` / `unmuteMicrophone()` / `startScreenShare()`。

### 集成检查点
- 当前 slice 常与 `conference/participant-management`、`conference/room-chat`、`conference/screen-share` 联动。
- 集成方式通常为新增房主管理面板和成员态提示，不需要修改底层会控实现。
- 如果业务还有企业合规或审计要求，建议把重要会控动作同步记录到业务日志系统。

## 验证矩阵
| 层级 | 检查项 | 验证手段 | 预期结果 |
|------|--------|----------|---------|
| 1. 编译级 | 已导入 `useRoomParticipantState` / `DeviceType` | 检查 `import` 语句 | 会控相关 API 可解析 |
| 2. 静态规则级 | 会控动作、toggle 文案与成员端反馈都有体现 | 搜索会控 API、状态回显与按钮文案派生逻辑 | 形成“控制 + 感知 + 管理端回显”闭环 |
| 3. 运行时级 | 房主 / 管理员可成功发起会控并解除会控 | 在高权限账号下执行开启 / 解除操作 | 会控成功广播到成员端，且管理端按钮态正确切换 |
| 4. 业务行为级 | 刷新后管理端与被控成员都能看到一致状态 | 刷新管理端页面并用被控制账号观察页面 | 房间级规则不因页面刷新丢失，设备 / 聊天 / 共享入口状态持续正确 |
