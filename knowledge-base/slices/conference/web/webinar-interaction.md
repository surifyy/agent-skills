---
id: conference/webinar-interaction
platform: web
---

# Webinar 举手、上台与弹幕互动 — Web 实现

## 前置条件

**通用依赖**：见 [login-auth 平台 slice](../login-auth.md)。

**额外依赖**：
- 已安装 `tuikit-atomicx-vue3@latest`
- Webinar 房间应使用 `RoomType.Webinar` 创建或加入。

## 代码示例

### 观众举手与取消举手

```ts
import { ref, onMounted, onUnmounted } from 'vue';
import {
  DeviceType,
  RoomParticipantEvent,
  useRoomParticipantState,
} from 'tuikit-atomicx-vue3/room';

const {
  requestToOpenDevice,
  cancelOpenDeviceRequest,
  subscribeEvent,
  unsubscribeEvent,
} = useRoomParticipantState();

const isRaised = ref(false);

export async function toggleRaiseHand() {
  if (isRaised.value) {
    await cancelOpenDeviceRequest({ device: DeviceType.Microphone });
    isRaised.value = false;
    return;
  }

  await requestToOpenDevice({ device: DeviceType.Microphone, timeout: 30 });
  isRaised.value = true;
}

const resetRaised = () => {
  isRaised.value = false;
};

onMounted(() => {
  subscribeEvent(RoomParticipantEvent.onDeviceRequestApproved, resetRaised);
  subscribeEvent(RoomParticipantEvent.onDeviceRequestRejected, resetRaised);
  subscribeEvent(RoomParticipantEvent.onDeviceRequestTimeout, resetRaised);
});

onUnmounted(() => {
  unsubscribeEvent(RoomParticipantEvent.onDeviceRequestApproved, resetRaised);
  unsubscribeEvent(RoomParticipantEvent.onDeviceRequestRejected, resetRaised);
  unsubscribeEvent(RoomParticipantEvent.onDeviceRequestTimeout, resetRaised);
});
```

### 主持人处理举手列表

```ts
import { computed } from 'vue';
import { useRoomParticipantState, type DeviceRequestInfo } from 'tuikit-atomicx-vue3/room';

const {
  pendingDeviceApplications,
  promoteToParticipant,
  approveOpenDeviceRequest,
  rejectOpenDeviceRequest,
} = useRoomParticipantState();

const pendingCount = computed(() => pendingDeviceApplications.value.length);

export async function approveRaiseHand(invitation: DeviceRequestInfo) {
  await promoteToParticipant({ userId: invitation.senderUserId });
  await approveOpenDeviceRequest({
    device: invitation.deviceType,
    userId: invitation.senderUserId,
  });
}

export async function rejectRaiseHand(invitation: DeviceRequestInfo) {
  await rejectOpenDeviceRequest({
    device: invitation.deviceType,
    userId: invitation.senderUserId,
  });
}
```

### Webinar 弹幕入口

```vue
<template>
  <BarrageList class="message-list" />
  <BarrageInput
    class="message-input"
    :disabled="localParticipant?.isMessageDisabled"
  />
</template>

<script setup lang="ts">
import { BarrageInput, BarrageList } from 'tuikit-atomicx-vue3/live';
import { useRoomParticipantState } from 'tuikit-atomicx-vue3/room';

const { localParticipant } = useRoomParticipantState();
</script>
```

## 平台特有注意事项

### 1. 举手不是直接开麦
观众端只发起 `requestToOpenDevice()`，真实上台和设备批准由主持人/管理员处理。不要在观众点击举手后直接调用 `openLocalMicrophone()`。

### 2. 接受申请要处理错误码
嘉宾人数已满或权限不足时，`promoteToParticipant()` / `approveOpenDeviceRequest()` 可能失败。遇到 `ERR_ALL_SEAT_OCCUPIED` 和 `ERR_NO_PERMISSION` 时应给出明确提示。

### 3. 弹幕和普通会议聊天不同源
普通会议聊天使用 `tuikit-atomicx-vue3/chat` 的 `setActiveConversation(GROUP${roomId})`；Webinar 弹幕使用 `tuikit-atomicx-vue3/live` 的 `BarrageList`、`BarrageInput`、`useBarrageState()`。

## 代码生成约束

### MUST

1. **观众举手使用 `requestToOpenDevice({ device: DeviceType.Microphone })`**。  
   **Verify**: 检查是否存在 `requestToOpenDevice`。
2. **主持人接受申请时先 `promoteToParticipant()` 再 `approveOpenDeviceRequest()`**。  
   **Verify**: 检查接受处理函数里的调用顺序。
3. **监听 approved/rejected/timeout 事件重置举手状态**。  
   **Verify**: 检查 `RoomParticipantEvent.onDeviceRequest*` 监听。
4. **Webinar 弹幕使用 live barrage 组件或状态**。  
   **Verify**: 检查是否从 `tuikit-atomicx-vue3/live` 导入 `BarrageInput` / `BarrageList` / `useBarrageState`。

### MUST NOT

1. **不要让观众举手后直接开麦**。  
   **Verify**: 检查观众举手函数中是否直接调用 `openLocalMicrophone()`。
2. **不要用普通会议聊天会话替代 Webinar 弹幕**。  
   **Verify**: Webinar 弹幕代码中不应只出现 `setActiveConversation(GROUP${roomId})`。

## 验证矩阵

| 层级 | 检查项 | 验证手段 | 预期结果 |
|------|--------|----------|---------|
| 1. 编译级 | Webinar 相关 API 可解析 | 检查 `DeviceType`、`RoomParticipantEvent`、barrage 导入 | 类型可解析 |
| 2. 静态规则级 | 接受举手顺序正确 | 阅读 `approveRaiseHand()` | 先上台再批准设备 |
| 3. 运行时级 | 观众举手和取消可用 | 双账号 Webinar 联调 | 主持人侧出现待处理申请 |
| 4. 业务行为级 | 弹幕禁言联动正确 | 禁言后尝试发送 | 输入或发送被拦截 |
