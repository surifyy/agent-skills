---
id: conference/webinar-interaction
name: Webinar 举手、上台与弹幕互动
product: conference
tags: [webinar, raise-hand, audience, participant, barrage, requestToOpenDevice]
related: [conference/room-config, conference/participant-management, conference/room-moderation, conference/room-chat]
---

# Webinar 举手、上台与弹幕互动

## 功能说明

Webinar 互动负责研讨会房型中的观众举手、主持人审批、观众上台成为嘉宾、设备申请收口以及弹幕互动。它解决的是“观众如何申请发言、主持人如何处理申请、观众区如何低成本互动”，不是普通 Standard 会议的成员管理入口。

Conference Core 中，观众举手本质上是 `requestToOpenDevice({ device: DeviceType.Microphone })`；主持人侧通过 `pendingDeviceApplications` 展示待处理申请，接受时先 `promoteToParticipant()`，再 `approveOpenDeviceRequest()`。

## 核心概念

| 能力 | 说明 |
|------|------|
| `RoomType.Webinar` | 研讨会房型，区分房主/管理员、嘉宾和观众 |
| 观众举手 | 观众申请打开麦克风，进入待审批队列 |
| `pendingDeviceApplications` | 主持人或管理员侧看到的设备申请列表 |
| 上台 | 观众被提升为嘉宾/参会人后才能参与发言或开设备 |
| 弹幕 | Webinar 低门槛互动入口，通常基于 live barrage 状态和组件 |
| 禁言联动 | 弹幕输入和普通聊天一样需要联动 `localParticipant.isMessageDisabled` |

## 最佳实践

### ✅ ALWAYS

1. **只在 Webinar 房型中启用举手和弹幕入口** —— Standard 会议优先使用成员管理和会中聊天。
2. **观众端举手用 `requestToOpenDevice({ device: DeviceType.Microphone })`** —— 不要让观众直接 `openLocalMicrophone()` 绕过审批。
3. **主持人接受申请时先上台再批准设备** —— 推荐顺序是 `promoteToParticipant()` → `approveOpenDeviceRequest()`。
4. **拒绝、超时、已批准都要清理观众端举手状态** —— 避免按钮一直显示“已举手”。
5. **弹幕输入必须联动禁言状态** —— `localParticipant.isMessageDisabled` 生效时，输入框和发送链路都要禁用。
6. **弹幕未读数只在面板关闭时累积** —— 打开面板应清零，并在切房间时重置。

### ❌ NEVER

1. **不要把 Webinar 观众当作普通会议成员直接开麦/开摄** —— 观众发言必须经过申请和审批。
2. **不要只批准设备而不提升角色** —— 观众仍可能没有上台权限，导致申请看似通过但设备不可用。
3. **不要把 Webinar 弹幕直接套用普通会议 `GROUP${roomId}` 聊天逻辑** —— Webinar 弹幕应使用 live barrage 能力。

## 排障指南

| 问题 | 表现 | 处理建议 |
|------|------|----------|
| 观众举手后主持人看不到 | 待处理列表为空 | 检查是否在 Webinar 房型、是否调用 `requestToOpenDevice()` |
| 主持人同意后观众仍不能发言 | 申请通过但麦克风不可用 | 检查是否先调用 `promoteToParticipant()` 再批准设备 |
| 举手按钮状态不复位 | 拒绝或超时后仍显示已举手 | 监听 approved/rejected/timeout 事件并重置本地状态 |
| 弹幕被禁言仍可输入 | UI 和真实权限不一致 | 绑定 `localParticipant.isMessageDisabled` 并拦截发送 |

## 关联知识

- **[conference/participant-management](participant-management.md)** —— 角色提升、管理员和成员治理。
- **[conference/room-moderation](room-moderation.md)** —— 禁言、禁设备等会控规则。
- **[conference/room-chat](room-chat.md)** —— 普通会议聊天，与 Webinar 弹幕需要区分。
