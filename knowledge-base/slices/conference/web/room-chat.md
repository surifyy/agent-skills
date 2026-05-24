---
id: conference/room-chat
platform: web
api_docs:
  - title: 会中聊天
    url: https://cloud.tencent.com/document/product/647/126933
---

# 会中聊天 — Web 实现

## 前置条件
**通用依赖**：见 [login-auth 平台 slice](../login-auth.md)。

**额外依赖**：
- 已安装 `tuikit-atomicx-vue3@latest`
- 若采用富文本编辑器集成，可按需接入 `@tiptap/vue-3`；若只使用原生 `<input>` / `<textarea>`，不需要依赖编辑器实例。

**前置状态**：
- 已阅读 `conference/room-chat`，明确当前能力的产品边界。
- 已完成 `conference/login-auth`，确保当前页面具备稳定登录态。
- 已根据业务流程接入会议上下文，并能从 `useRoomState()` 获取有效 `currentRoom.roomId`。

## 接入方式
当前文档仅覆盖**无 UI 集成**：聊天列表、输入区、抽屉 / 侧栏样式均由业务自己实现，`tuikit-atomicx-vue3` 负责提供房间聊天相关 Hook、State 与发送能力。以下内容以 `会中聊天（Web）.md` 中 **“方案二：使用底层 API 自定义集成”** 为主。

> **注意**：
> `MessageInputState` 默认支持与 `@tiptap/vue-3` 编辑器集成。如果您仅需要简单的文本输入框（例如 `<input>` 或 `<textarea>`），请忽略 `setEditorInstance()`、`setContent()` 等与编辑器实例绑定的 API，直接使用 `updateRawValue()` 和 `sendMessage()` 即可。

## 代码示例
### 步骤一：数据初始化

在用户加入房间成功后，需要调用 `setActiveConversation()` 初始化聊天数据。建议监听 `currentRoom` 的变化来自动处理。

```ts
import { onUnmounted, watch } from 'vue';
import { useConversationListState } from 'tuikit-atomicx-vue3/chat';
import { useRoomState } from 'tuikit-atomicx-vue3/room';

const { currentRoom } = useRoomState();
const { setActiveConversation } = useConversationListState();

watch(() => currentRoom.value?.roomId, (roomId) => {
  if (!roomId) {
    setActiveConversation('');
    return;
  }

  setActiveConversation(`GROUP${roomId}`);
}, { immediate: true });

onUnmounted(() => {
  setActiveConversation('');
});
```

> **说明**：
> - `GROUP` 为固定前缀，`setActiveConversation()` 参数必须为 `GROUP${roomId}`，否则无法正常收发消息。
> - 在房间切换、退房或聊天按钮组件卸载时，应同步 `setActiveConversation('')` 清空旧会话，避免消息错发至错误会话。

### 步骤二：获取消息列表

使用 `useMessageListState()` 获取当前会话的消息列表，`messageList` 是响应式数据，会自动更新新收到的消息。

```ts
import { useMessageListState } from 'tuikit-atomicx-vue3/chat';

const {
  messageList,
  loadMoreOlderMessage,
  hasMoreOlderMessage,
} = useMessageListState();

console.log(messageList.value);
console.log(hasMoreOlderMessage.value);
```

### 步骤三：发送消息

使用 `useMessageInputState()` 管理输入框内容并发送消息。

```ts
import { computed } from 'vue';
import { useMessageInputState } from 'tuikit-atomicx-vue3/chat';
import { useRoomParticipantState } from 'tuikit-atomicx-vue3/room';

const {
  inputRawValue,
  updateRawValue,
  sendMessage,
} = useMessageInputState();

const { localParticipant } = useRoomParticipantState();
const isMessageDisabled = computed(() => Boolean(localParticipant.value?.isMessageDisabled));
const hasTextInput = computed(() => (
  typeof inputRawValue.value === 'string'
    ? inputRawValue.value.trim().length > 0
    : inputRawValue.value.length > 0
));

const handleSend = async () => {
  if (isMessageDisabled.value) return;
  if (!hasTextInput.value) return;

  try {
    await sendMessage();
    updateRawValue('');
  } catch (error) {
    console.error('发送失败', error);
  }
};

// 原生输入框示例
// <input
//   :value="inputRawValue"
//   @input="(e) => updateRawValue((e.target as HTMLInputElement).value)"
//   @keyup.enter="handleSend"
// />
```

> **说明**：
> - 非富文本模式下，发送成功后请使用 `updateRawValue('')` 清空输入框。
> - 若当前成员已被禁言，除了输入框应禁用外，发送链路也需要一起拦截。
> - 若需要直接发送富媒体消息，可通过 `sendMessage(InputContent[])` 传入图片、文件等内容。

### 步骤四：加载历史消息

通过 `loadMoreOlderMessage()` 分页拉取历史消息，通常在滚动到列表顶部时触发。

```ts
import { nextTick } from 'vue';
import { useMessageListState } from 'tuikit-atomicx-vue3/chat';

const {
  hasMoreOlderMessage,
  loadMoreOlderMessage,
} = useMessageListState();

const loadHistory = async (scrollContainer: HTMLElement) => {
  if (!hasMoreOlderMessage.value) return;

  const previousHeight = scrollContainer.scrollHeight;
  await loadMoreOlderMessage();

  await nextTick();
  const currentHeight = scrollContainer.scrollHeight;
  scrollContainer.scrollTop += currentHeight - previousHeight;
};
```

> **注意**：
> 加载历史消息后，通常需要手动调整滚动条位置，以保持当前浏览视角不发生跳变。

### 步骤五：高级功能（已读回执）

如果业务需要已读回执功能，可以通过 `setEnableReadReceipt()` 开启。

```ts
import { useMessageListState } from 'tuikit-atomicx-vue3/chat';

const {
  setEnableReadReceipt,
} = useMessageListState();

setEnableReadReceipt(true);
```

## 调用时序
```
完成 login-auth
   │
   ▼
进入 room-lifecycle，拿到 currentRoom.roomId
   │
   ▼
调用 setActiveConversation(`GROUP${roomId}`)
   │
   ├─ 成功 → 获取 messageList / inputRawValue 等状态并渲染业务自定义聊天 UI
   ├─ 房间切换 → 重新绑定新的 GROUP 会话
   └─ 失败 → 提示会话初始化异常并阻止发言入口
   │
   ▼
结合 localParticipant.isMessageDisabled 控制输入区与发送链路
   │
   ▼
处理发送、历史消息、可选已读回执与富媒体消息
   │
   ▼
退房或结束会议后收口聊天入口、旧会话上下文与本地状态
```

## 平台特有注意事项
### 1. 会议聊天依赖 `GROUP${roomId}` 规则
会中聊天基于 IM 群组会话，`setActiveConversation()` 必须使用 `GROUP${roomId}`，不能只传裸 `roomId`。

### 2. 使用原生输入框时优先走 `updateRawValue()`
若没有接入富文本编辑器，请直接使用 `updateRawValue()` 和 `sendMessage()`；不要依赖 `setContent()`、`setEditorInstance()` 这类编辑器绑定 API 来维护普通输入框内容。

### 3. 输入区应直接绑定会控禁言状态
若 `localParticipant.isMessageDisabled` 已经生效，聊天输入框必须立即转为禁用或只读；自定义输入框同样需要在发送前再次拦截。

### 4. 自定义消息列表容器必须具备稳定高度
聊天区通常需要独立滚动容器；如果父容器没有固定高度并且缺少 `overflow: hidden` 或等价约束，消息区容易无限拉长、无法滚动。

### 5. 历史消息加载后要恢复滚动位置
自定义聊天面板调用 `loadMoreOlderMessage()` 后，通常需要在 DOM 更新后修正 `scrollTop`，避免阅读位置跳变。

### 6. 抽屉式聊天需要维护未读累积与清零
如果聊天面板平时折叠或关闭，应在关闭时累计未读、打开时清零；首次初始化消息列表时不要误计入未读。

### 7. 富媒体消息和已读回执属于可选高级能力
图片、文件等消息可通过 `sendMessage(InputContent[])` 发送；如有消息确认诉求，可结合 `setEnableReadReceipt(true)` 开启已读回执。

### 8. 自定义渲染时要覆盖不同消息类型分支
`messageList` 中通常会出现文本、图片、文件等不同类型消息；自定义聊天 UI 需要按消息类型分别渲染，不要只按纯文本分支处理。

## 常见错误与场景对照

| 错误 / 场景 | 常见触发时机 | 建议处理方式 |
|-------------|--------------|--------------|
| 会话绑定成裸 `roomId` | 只拿到房间号就直接调用 `setActiveConversation(roomId)` | 改为固定用 `setActiveConversation()` 绑定 `GROUP${roomId}` |
| 进房前就切会话 | 登录或进房尚未完成时初始化聊天 | 等 `currentRoom.roomId` 有值后再绑定会话 |
| 原生输入框改了值但发送仍为空 | 直接操作输入框值，没有调用 `updateRawValue()` | 使用 `updateRawValue()` 维护输入内容，再调用 `sendMessage()` |
| 输入框禁用了但代码仍能发送 | 只做 UI 禁用，没有拦截发送函数 | 发送前再次校验禁言状态，保持 UI 与真实行为一致 |
| 自定义聊天区没有稳定高度 | 侧栏 / 抽屉只渲染了内容，没有约束滚动区域 | 为消息列表父容器提供固定高度、滚动区或等价布局约束 |
| 聊天抽屉首次打开就显示未读 | 初次拉取历史消息被误算成新消息 | 仅在窗口关闭且新消息长度增长时累计未读 |
| 历史消息加载后界面跳动 | 上滑加载更早消息时滚动位置漂移 | 记录加载前高度，加载后按高度差恢复滚动位置 |
| 富媒体消息显示异常 | 自定义 UI 只按文本消息渲染 | 按消息类型拆分渲染逻辑，覆盖文本、图片、文件等分支 |

## 代码生成约束
### 编译必要条件
- **通用条件**：见 [login-auth 平台 slice](../login-auth.md)。
- **额外导入**：至少需要从 `tuikit-atomicx-vue3/chat` 导入 `useConversationListState`；自定义聊天通常还需要 `useMessageListState` 与 `useMessageInputState`；若输入区需要联动禁言态，通常还需要 `useRoomParticipantState`。
- **运行前提**：当前用户已完成登录，且已拿到有效 `roomId`。
- **容器前提**：业务自定义消息列表时，应提供稳定高度与独立滚动区域。

### 生成规则
#### MUST（生成时必须包含）

1. **用 `currentRoom.roomId` 驱动当前聊天会话** — 这样会议切换时会话才能同步收口。  
   **Verify**: 检查是否从 `useRoomState()` 读取 `currentRoom`。
2. **通过 `setActiveConversation()` 绑定 `GROUP${roomId}` 群会话** — 这是会中聊天的关键映射关系。  
   **Verify**: 搜索是否存在 `GROUP${roomId}` 或等价拼接逻辑。
3. **用 `useMessageListState()` 驱动消息列表和历史消息加载** — 保持当前会话数据源一致。  
   **Verify**: 检查是否读取 `messageList`，并按需使用 `loadMoreOlderMessage()`。
4. **自定义原生输入框时使用 `updateRawValue()` 与 `sendMessage()`** — 保持状态同步和发送行为一致。  
   **Verify**: 检查是否通过 `updateRawValue()` 维护输入内容，并在发送后清空。
5. **把禁言状态同时接到输入区和真实发送链路** — 不能只做视觉禁用。  
   **Verify**: 检查输入区是否联动 `isMessageDisabled`，且发送前有同源校验。
6. **为自定义消息列表提供稳定滚动容器** — 否则聊天区很容易出现拉伸和滚动异常。  
   **Verify**: 检查聊天区父容器是否具备固定高度、滚动区或等价布局约束。

#### MUST NOT（生成时绝不能出现）

1. **不要把房间聊天直接绑定为裸 `roomId` 或私聊会话** — 会导致消息进错会话。  
   **Verify**: 检查会话 ID 是否符合 `GROUP${roomId}` 规则。
2. **不要忽略禁言状态继续开放输入框或发送动作** — UI 与真实可发言状态会不一致。  
   **Verify**: 检查输入区和发送函数是否都联动禁言状态。
3. **不要在没有高度约束的容器里渲染自定义消息列表** — 很容易导致列表无法正常滚动。  
   **Verify**: 检查父容器是否具备固定高度或 `height: 100%` 等稳定布局。
4. **不要把首次历史消息加载误算成未读消息** — 会让角标在初始化后立刻脏掉。  
   **Verify**: 检查未读逻辑是否区分初始化加载与真实新消息。
5. **不要在原生输入场景下依赖富文本编辑器 API 清空内容** — 没绑定编辑器时不会按预期生效。  
   **Verify**: 检查普通输入框场景是否使用 `updateRawValue('')` 而不是 `setContent('')`。

### 集成检查点
- 当前 slice 强依赖 `conference/room-lifecycle` 与 `conference/login-auth`。
- 聊天接入通常是新增侧栏、抽屉或右侧协作区，不需要修改 SDK 内部 IM 实现。
- 如果业务已经有独立 IM 会话体系，需要明确会议群会话与业务私聊的切换边界。
- 如果产品需要图片、文件、已读回执等高级能力，优先在自定义聊天方案里统一规划消息类型和渲染分支。

## 验证矩阵
| 层级 | 检查项 | 验证手段 | 预期结果 |
|------|--------|----------|---------|
| 1. 编译级 | 已导入房间与聊天相关 Hook | 检查 `import` 语句 | Room / Chat Hook 可解析 |
| 2. 静态规则级 | 会话 ID 符合 `GROUP${roomId}` 规则 | 搜索 `setActiveConversation` 调用 | 存在群会话绑定逻辑 |
| 3. 数据流级 | 已读取消息列表、输入内容与禁言状态 | 检查 `useMessageListState`、`useMessageInputState`、`useRoomParticipantState` 调用 | 聊天数据源与权限源清晰 |
| 4. 结构级 | 自定义聊天列表具备稳定高度容器与滚动区域 | 检查模板结构与样式容器 | 消息列表具备稳定滚动空间 |
| 5. 运行时级 | 进入会议后聊天面板可展示正确会话 | 进房并打开聊天面板 | 消息收发落在当前会议会话 |
| 6. 业务行为级 | 禁言、历史消息、富媒体渲染表现正确 | 切换禁言、上滑加载历史、发送图片文件 | 输入区、滚动位置和不同消息类型表现符合预期 |
