---
id: live/device-control
name: 设备管理
product: live
tags: [camera, microphone, device, DeviceStore, permission]
platforms: [ios, android, web, flutter]
related: [live/login-auth, live/anchor-preview, live/coguest-apply]
docs:
  - title: 搭建视频直播
    url: https://trtc.io/zh/document/74594
---

# 设备管理

## 功能说明

`DeviceStore` 是全局单例，统一管理摄像头和麦克风的生命周期。所有主播推流、连麦等场景均通过 `DeviceStore` 完成本地设备的打开、关闭与切换操作。

`DeviceStore` 依赖 `LoginStore` 的登录态，必须在登录成功后才可调用其接口。

## 核心概念

| 方法 / 属性 | 说明 |
|-------------|------|
| `DeviceStore.shared` | 全局单例，整个 App 生命周期内唯一实例 |
| `openLocalCamera(isFront:completion:)` | 打开本地摄像头；`isFront: true` 使用前置摄像头，`false` 使用后置 |
| `closeLocalCamera()` | 关闭本地摄像头，释放硬件资源 |
| `openLocalMicrophone(completion:)` | 打开本地麦克风并开始采集音频 |
| `closeLocalMicrophone()` | 关闭本地麦克风，停止音频采集 |
| `switchCamera(isFront:)` | 在不关闭摄像头的情况下切换前后摄像头 |

## 最佳实践

### ✅ ALWAYS

1. **先检查权限再打开设备** — 调用 `openLocalCamera` / `openLocalMicrophone` 前，通过系统 `AVCaptureDevice.authorizationStatus` 确认权限已授予。权限被拒时引导用户前往系统设置，而非直接调用 SDK 方法（会触发 `-1101` / `-1105`）。
2. **不用时关闭设备释放资源** — 主播退出直播间或 App 进入后台时调用 `closeLocalCamera()` 与 `closeLocalMicrophone()`，避免摄像头指示灯常亮、电量消耗过快，以及被系统强制中断。
3. **连麦结束后及时关闭** — 观众连麦场景中，连麦结束（下麦）后立即关闭摄像头与麦克风，避免麦克风一直采集影响用户隐私体验。

### ❌ NEVER

1. **未登录时操作设备** — 在 `LoginStore` 登录成功之前调用 `DeviceStore` 接口会返回 `-1002`，设备不会正常打开。
2. **忽略权限被拒回调** — `completion` 中的 `.failure` 分支（尤其是 `-1101` 摄像头缺授权 / `-1105` 麦克风缺授权）必须处理，向用户展示引导弹窗或跳转系统设置入口，否则用户会看到黑屏或无声直播。

## 排障指南

### 常见错误码

| 错误码 | 描述 | 处理建议 |
|--------|------|----------|
| `-1100` | 打开摄像头失败（系统/硬件层面） | 检查设备是否完好；重启 App 重试 |
| `-1101` | 摄像头缺少系统授权 | 引导用户在「设置 > 隐私 > 摄像头」中开启权限 |
| `-1102` | 摄像头被其他进程占用 | 提示用户关闭其他使用摄像头的应用（如 FaceTime） |
| `-1103` | 设备无摄像头 | 模拟器场景；提示用户使用真机测试 |
| `-1104` | 打开麦克风失败（系统/硬件层面） | 检查设备是否完好；重启 App 重试 |
| `-1105` | 麦克风缺少系统授权 | 引导用户在「设置 > 隐私 > 麦克风」中开启权限 |
| `-1106` | 麦克风被其他进程占用 | 关闭其他音频应用（电话、语音通话等） |
| `-1107` | 设备无麦克风 | 检查外接麦克风连接状态 |

### 排障流程

```
摄像头打不开
├── 错误码 -1101（缺授权）
│   ├── 首次使用 → 系统弹窗未弹出？
│   │       └─ 检查 Info.plist 是否有 NSCameraUsageDescription
│   └── 已拒绝 → 引导用户前往「设置 > 隐私 > 摄像头」手动开启
├── 错误码 -1102（被占用）
│   └─ 提示用户关闭其他正在使用摄像头的应用
├── 错误码 -1103（无摄像头）
│   └─ 模拟器不支持摄像头，切换到真机测试
├── 错误码 -1100（打开失败）
│   ├── 重启 App 重试
│   └── 持续失败 → 抓取 error.message 上报
└── 出现黑屏但无错误码
    ├── 是否在 openLocalCamera 完成前就渲染了视图？→ 等待 completion 回调
    └── 检查视图层级是否正确（预览 View 是否 addSubview）

麦克风打不开
├── 错误码 -1105（缺授权）→ 引导前往「设置 > 隐私 > 麦克风」
├── 错误码 -1106（被占用）→ 关闭系统电话 / 其他语音应用
├── 错误码 -1107（无麦克风）→ 检查外接设备
└── 错误码 -1104（打开失败）→ 重试或上报
```

## 关联知识

- **[live/login-auth](live/login-auth.md)** — DeviceStore 依赖登录态，需先完成登录
- **[live/anchor-preview](live/anchor-preview.md)** — 摄像头打开后进行主播预览渲染
- **[live/coguest-apply](live/coguest-apply.md)** — 连麦场景下观众需打开摄像头与麦克风
- **[live/error-codes](live/error-codes.md)** — 完整设备错误码参考
