---
id: conference/screen-share
platform: web
api_docs:
  - title: 屏幕分享
    url: https://cloud.tencent.com/document/product/647/126925
---

# 屏幕分享 — Web 实现

## 前置条件
**通用依赖**：见 [login-auth 平台 slice](../login-auth.md)。

**额外依赖**：
- 已安装 `tuikit-atomicx-vue3@latest`

**前置状态**：
- 已阅读 `conference/screen-share`，明确当前能力的产品边界。
- 已完成 `conference/login-auth`，确保当前页面具备稳定登录态。
- 已根据业务流程接入会议上下文；需要房间状态时，优先通过 `conference/room-lifecycle` 统一承接。
- 当前能力涉及媒体采集、渲染或浏览器权限时，请在 `HTTPS` 或 `localhost` 安全上下文下调试。

## 代码示例
### 基础接入：开始共享、监听共享者并在结束时收口

```ts
import { watch } from 'vue';
import { useDeviceState, useRoomParticipantState } from 'tuikit-atomicx-vue3/room';

const { startScreenShare, stopScreenShare, screenStatus } = useDeviceState();
const { participantWithScreen } = useRoomParticipantState();

await startScreenShare({ screenAudio: true });
watch(participantWithScreen, (participant) => {
  console.log('当前共享者:', participant?.userId);
});
await stopScreenShare();
```

## 调用时序
```
完成 login-auth 并进入会议
   │
   ▼
调用 startScreenShare({ screenAudio })
   │
   ├─ 浏览器弹出原生共享选择器
   ├─ 用户确认 → 本地开始共享，participantWithScreen 更新
   ├─ 用户取消 → 保持未共享状态
   └─ 浏览器原生停止 → screenStatus / participantWithScreen 变化收口 UI
   │
   ▼
需要结束共享时调用 stopScreenShare()
```

## 平台特有注意事项
### 1. 系统音频共享受浏览器差异影响明显
`screenAudio` 在 Chrome / Edge 上通常体验更完整，Firefox / Safari 的能力与限制差异更大，联调时要分浏览器验证。

### 2. 必须处理浏览器原生“停止分享”
用户点击浏览器原生停止按钮后，前端不能只依赖业务按钮状态，必须通过共享状态变化主动收口 UI。

### 3. 屏幕分享主要面向桌面浏览器
移动端 Web 对屏幕共享的支持极其有限，产品设计和文档说明都应以桌面场景为主。

### 4. 本地共享 tile 不展示真实预览时，不要让它停留在纯黑屏
部分 Web 环境或产品方案里，本地共享流不会展示真实预览，或者业务上本来就不希望在本地重复渲染共享内容。此时推荐改成“您正在共享屏幕”一类的示意态，并按需提供“结束共享”操作。

这里的图标、文案、按钮布局都只是**示例**，不应被理解为固定 UI 规范；真正需要固定的是：用户一眼能知道自己正在共享，且不会看到无语义的黑底。

如需具体承载方式，优先交给 `conference/web/video-layout` 中的 `participantViewUI` 或页面级 overlay 处理。

## 代码生成约束
### 编译必要条件
- **通用条件**：见 [login-auth 平台 slice](../login-auth.md)。
- **额外导入**：至少需要导入 `useDeviceState` 与 `useRoomParticipantState`。
- **运行前提**：浏览器支持屏幕采集，并处于安全上下文。

### 生成规则
#### MUST（生成时必须包含）

1. **通过 `startScreenShare()` / `stopScreenShare()` 控制共享主链路** — 可保证共享状态与房间状态一致。  
   **Verify**: 检查是否存在 `startScreenShare(` 与 `stopScreenShare(`。
2. **根据 `participantWithScreen` 或 `screenStatus` 驱动 UI** — 共享者变化必须能被页面感知。  
   **Verify**: 检查是否读取 `participantWithScreen` 或 `screenStatus`。
3. **如果本地共享流不展示真实预览或表现为黑底，必须补共享中的提示态** —— 可以是状态文案、图标、结束共享入口或它们的组合，但不能只有无语义黑屏。  
   **Verify**: 检查本地共享中的 UI 是否至少向用户表达“正在共享”这一状态。

#### MUST NOT（生成时绝不能出现）

1. **不要假设所有浏览器都等价支持系统音频共享** — 会造成错误的产品承诺。  
   **Verify**: 检查是否有浏览器差异说明或降级策略。
2. **不要忽略浏览器原生停止共享后的状态变化** — UI 会残留“仍在共享”的假状态。  
   **Verify**: 检查是否有基于状态变化的收口逻辑。
3. **不要把共享中的示意态写死成唯一视觉规范** —— 示例可以参考设计稿，但实现必须允许按业务风格调整。  
   **Verify**: 检查说明文字是否把示例样式当作唯一合法 UI。

### 集成检查点
- 当前 slice 常与 `conference/video-layout`、`conference/room-moderation` 联动。
- 集成方式通常是新增共享按钮、共享状态提示和主画面切换逻辑。
- 如果业务需要限制谁能共享，应在上层与角色治理或会控规则联合判断。

## 验证矩阵
| 层级 | 检查项 | 验证手段 | 预期结果 |
|------|--------|----------|---------|
| 1. 编译级 | 已导入共享相关 Hook | 检查 `import` 语句 | 屏幕共享 API 可解析 |
| 2. 静态规则级 | 共享开始、停止和状态监听都存在 | 搜索 `startScreenShare` / `stopScreenShare` / `participantWithScreen` | 形成完整共享链路 |
| 3. 运行时级 | 浏览器确认后可开始共享 | 在桌面浏览器执行共享 | 页面出现共享状态 |
| 4. 业务行为级 | 原生停止共享后 UI 正确收口 | 点击浏览器原生停止按钮 | 共享按钮与主画面状态恢复正常 |
