---
id: conference/ai-tools
name: AI 实时转写与字幕
product: conference
tags: [ai, asr, transcription, subtitle, translation, realtime]
related: [conference/room-lifecycle, conference/participant-management]
---

# AI 实时转写与字幕

## 功能说明

AI 实时转写与字幕负责会议中的实时语音转文字、字幕展示、翻译语言设置和转写消息列表。业务 UI 可以把它做成工具栏入口、侧栏面板或浮层字幕；房主负责启动和更新转写配置，其他成员主要消费字幕和消息结果。

## 核心概念

| 能力 | 说明 |
|------|------|
| `useAITranscriberState()` | 启停和更新实时转写配置 |
| `startRealtimeTranscriber()` | 启动实时转写，传入源语言和翻译目标语言 |
| `stopRealtimeTranscriber()` | 停止实时转写，离房或角色变化时需要收口 |
| `updateRealTimeTranscriber()` | 转写运行中更新语言配置 |
| `RealtimeTranscriberEvent` | 监听转写启动、停止等状态 |
| `Subtitle` | 字幕展示组件 |
| `RealtimeMessageList` | 实时转写消息列表组件 |
| `SubtitleDisplayMode` | 字幕展示模式，当前是 `'bilingual'` / `'translation'` 这类字符串类型 |

## 最佳实践

### ✅ ALWAYS

1. **AI 工具入口应由业务 UI 显式控制** —— 只有在当前会议和用户权限满足条件时才展示入口。
2. **只让房主启动或更新实时转写** —— 推荐用 `currentRoom.roomOwner.userId === localParticipant.userId` 判断管理权。
3. **打开字幕或转写面板前先确保 ASR 已启动** —— 面板消费的是实时转写状态，不应空开。
4. **监听转写停止事件并关闭相关 UI** —— ASR 停止后字幕和实时消息面板应同步收口。
5. **房间切换时重置语言、字幕模式和启动状态** —— 防止跨房间继承旧配置。
6. **处理套餐或权限类错误** —— 启动失败时要给出可理解提示，而不是只打印日志。

### ❌ NEVER

1. **不要让每个成员都尝试启动转写** —— 会造成重复请求、权限失败或状态混乱。
2. **不要在离房后保留字幕浮层** —— 旧房间的实时内容不应残留到下一场会议。
3. **不要只切 UI 语言而不调用 `updateRealTimeTranscriber()`** —— 运行中的转写配置不会自动变化。

## 排障指南

| 问题 | 表现 | 处理建议 |
|------|------|----------|
| 点击字幕后没有内容 | 字幕浮层打开但无文本 | 检查是否已调用 `startRealtimeTranscriber()` |
| 非房主启动失败 | 普通成员打开 AI 工具报错 | 只允许房主启动，其他成员消费已有转写结果 |
| 切换语言不生效 | 设置面板保存后字幕仍旧语言 | 转写已启动时调用 `updateRealTimeTranscriber()` |
| 离房后字幕残留 | 下一场会议仍显示旧字幕 | 监听 roomId 变化和 stopped 事件，清理 UI 状态 |

## 关联知识

- **[conference/room-lifecycle](room-lifecycle.md)** —— 进退房决定 AI 状态的初始化与清理时机。
- **[conference/participant-management](participant-management.md)** —— 房主身份和角色变化会影响 AI 管理权。
