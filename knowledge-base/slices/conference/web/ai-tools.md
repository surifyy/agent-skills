---
id: conference/ai-tools
platform: web
---

# AI 实时转写与字幕 — Web 实现

## 前置条件

**通用依赖**：见 [login-auth 平台 slice](../login-auth.md)。

**额外依赖**：
- 已安装 `tuikit-atomicx-vue3@latest`
- 已完成会议 UI 入口设计，例如工具栏按钮、侧栏面板或字幕浮层。

## 代码示例

### 启动、停止和更新实时转写

```ts
import { ref, watch } from 'vue';
import {
  RealtimeTranscriberEvent,
  useAITranscriberState,
  useRoomParticipantState,
  useRoomState,
} from 'tuikit-atomicx-vue3/room';
import type { SubtitleDisplayMode } from 'tuikit-atomicx-vue3/room';

const sourceLanguage = ref('auto');
const targetLanguage = ref('');
const subtitleDisplayMode = ref<SubtitleDisplayMode>('translation');
const hasStartedASR = ref(false);

const {
  startRealtimeTranscriber,
  stopRealtimeTranscriber,
  updateRealTimeTranscriber,
  subscribeEvent,
} = useAITranscriberState();

const { currentRoom } = useRoomState();
const { localParticipant } = useRoomParticipantState();

const canManageTranscriber = () =>
  currentRoom.value?.roomOwner?.userId === localParticipant.value?.userId;

subscribeEvent(RealtimeTranscriberEvent.onRealtimeTranscriberStarted, () => {
  hasStartedASR.value = true;
});

subscribeEvent(RealtimeTranscriberEvent.onRealtimeTranscriberStopped, () => {
  hasStartedASR.value = false;
});

export async function ensureASRStarted() {
  if (!canManageTranscriber() || hasStartedASR.value) return;

  await startRealtimeTranscriber({
    sourceLanguage: sourceLanguage.value || 'auto',
    translationLanguages: targetLanguage.value ? [targetLanguage.value] : [],
  });
  hasStartedASR.value = true;
}

export async function saveASRSettings(options: {
  sourceLanguage?: string;
  targetLanguage?: string;
  subtitleDisplayMode?: SubtitleDisplayMode;
}) {
  const nextSourceLanguage = options.sourceLanguage ?? sourceLanguage.value;
  const nextTargetLanguage = options.targetLanguage ?? targetLanguage.value;

  sourceLanguage.value = nextSourceLanguage;
  targetLanguage.value = nextTargetLanguage;
  subtitleDisplayMode.value = options.subtitleDisplayMode ?? subtitleDisplayMode.value;

  if (canManageTranscriber() && hasStartedASR.value) {
    await updateRealTimeTranscriber({
      sourceLanguage: sourceLanguage.value || 'auto',
      translationLanguages: targetLanguage.value ? [targetLanguage.value] : [],
    });
  }
}

export async function stopASR() {
  if (!hasStartedASR.value) return;
  await stopRealtimeTranscriber();
  hasStartedASR.value = false;
}

watch(() => currentRoom.value?.roomId, () => {
  sourceLanguage.value = 'auto';
  targetLanguage.value = '';
  hasStartedASR.value = false;
}, { immediate: true });
```

### 字幕浮层与实时转写消息列表

```vue
<template>
  <Subtitle
    v-if="isSubtitlesVisible"
    :target-language="targetLanguage"
    :display-mode="subtitleDisplayMode"
  />

  <RealtimeMessageList
    v-if="isRealtimeMessageListVisible"
    :target-language="targetLanguage"
    :display-mode="subtitleDisplayMode"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import {
  RealtimeMessageList,
  Subtitle,
} from 'tuikit-atomicx-vue3/room';
import type { SubtitleDisplayMode } from 'tuikit-atomicx-vue3/room';

const isSubtitlesVisible = ref(false);
const isRealtimeMessageListVisible = ref(false);
const targetLanguage = ref('');
const subtitleDisplayMode = ref<SubtitleDisplayMode>('translation');
</script>
```

## 平台特有注意事项

### 1. 管理权以房主为准
推荐只让房主启动或更新 ASR 配置。如果业务要放开给管理员，需要明确权限规则，并处理多人同时更新配置的冲突。

### 2. 打开 UI 前先启动 ASR
字幕浮层和转写消息列表只是展示层。点击入口时应先调用 `ensureASRStarted()`，成功后再打开字幕或侧栏。

### 3. 停止后同步关闭 UI
监听 `RealtimeTranscriberEvent.onRealtimeTranscriberStopped`，转写停止后关闭字幕、实时消息面板和设置弹层，避免残留。

### 4. 套餐错误要显式提示
启动实时转写可能返回套餐未开通、权限不足或频控类错误。遇到 `ERR_REQUIRE_PAYMENT` 时应提示需要开通对应套餐。

## 代码生成约束

### MUST

1. **通过 `useAITranscriberState()` 启停和更新转写**。  
   **Verify**: 检查是否存在 `startRealtimeTranscriber()` / `stopRealtimeTranscriber()`。
2. **打开字幕或转写面板前确保 ASR 已启动**。  
   **Verify**: 检查入口点击前是否调用 `ensureASRStarted()` 或等价逻辑。
3. **房间切换或转写停止时清理 UI 状态**。  
   **Verify**: 检查 `currentRoom.roomId` watch 或 `onRealtimeTranscriberStopped` 监听。
4. **运行中改语言时调用 `updateRealTimeTranscriber()`**。  
   **Verify**: 检查保存设置逻辑中是否调用更新接口。

### MUST NOT

1. **不要让每个参会人都启动 ASR**。  
   **Verify**: 检查是否有房主或业务权限判断。
2. **不要只渲染 `Subtitle` 而没有转写启动链路**。  
   **Verify**: 检查字幕入口是否能触发启动。

## 验证矩阵

| 层级 | 检查项 | 验证手段 | 预期结果 |
|------|--------|----------|---------|
| 1. 编译级 | AI 转写 API 可解析 | 检查 `useAITranscriberState`、`Subtitle` 导入 | 类型可解析 |
| 2. 静态规则级 | 启动、更新、停止链路完整 | 搜索 `startRealtimeTranscriber` / `updateRealTimeTranscriber` / `stopRealtimeTranscriber` | 三段链路存在 |
| 3. 运行时级 | 房主可打开字幕和转写列表 | 房主账号点击 AI 工具 | ASR 启动并展示内容 |
| 4. 业务行为级 | 切房间或停止后 UI 收口 | 离房或停止 ASR | 字幕和转写面板关闭 |
