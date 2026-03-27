---
id: live/device-control
platform: ios
---

# 设备管理 — iOS 实现

## 前置条件

**依赖安装（Podfile）**
```ruby
pod 'AtomicXCore', '~> 4.0'
```

**Info.plist 权限声明**（两项均须配置，否则系统拒绝授权或 App 崩溃）
```xml
<key>NSCameraUsageDescription</key>
<string>需要访问摄像头以进行视频直播</string>
<key>NSMicrophoneUsageDescription</key>
<string>需要访问麦克风以进行语音直播</string>
```

**前置状态**：
- `LoginStore.shared.isLogin == true`（登录成功后才可操作设备）
- 系统权限已授予（AVAuthorizationStatus == .authorized）

## API 调用

```swift
// 打开前/后置摄像头
DeviceStore.shared.openLocalCamera(
    isFront: Bool,
    completion: ((Result<Void, DeviceError>) -> Void)?
)

// 关闭摄像头
DeviceStore.shared.closeLocalCamera()

// 不中断采集情况下切换前后摄像头
DeviceStore.shared.switchCamera(isFront: Bool)

// 打开麦克风
DeviceStore.shared.openLocalMicrophone(
    completion: ((Result<Void, DeviceError>) -> Void)?
)

// 关闭麦克风
DeviceStore.shared.closeLocalMicrophone()
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `isFront` | `Bool` | `true` = 前置摄像头，`false` = 后置摄像头 |
| `completion` | `Result<Void, DeviceError>?` | 异步回调，在主线程返回；`nil` 表示不关心结果 |

## 代码示例

```swift
import AtomicXCore
import AVFoundation

/// 封装 DeviceStore 的完整设备管理类
final class DeviceManager {

    static let shared = DeviceManager()
    private init() {}

    // MARK: - 权限检查

    /// 检查摄像头权限状态
    func checkCameraPermission(completion: @escaping (Bool) -> Void) {
        switch AVCaptureDevice.authorizationStatus(for: .video) {
        case .authorized:
            completion(true)
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .video) { granted in
                DispatchQueue.main.async { completion(granted) }
            }
        case .denied, .restricted:
            completion(false)
        @unknown default:
            completion(false)
        }
    }

    /// 检查麦克风权限状态
    func checkMicrophonePermission(completion: @escaping (Bool) -> Void) {
        switch AVCaptureDevice.authorizationStatus(for: .audio) {
        case .authorized:
            completion(true)
        case .notDetermined:
            AVCaptureDevice.requestAccess(for: .audio) { granted in
                DispatchQueue.main.async { completion(granted) }
            }
        case .denied, .restricted:
            completion(false)
        @unknown default:
            completion(false)
        }
    }

    // MARK: - 摄像头操作

    /// 打开本地摄像头（含权限检查）
    func openCamera(isFront: Bool = true,
                    completion: @escaping (Result<Void, Error>) -> Void) {
        // 先检查权限
        checkCameraPermission { [weak self] granted in
            guard granted else {
                completion(.failure(DevicePermissionError.cameraNotAuthorized))
                return
            }
            // 权限已授予，调用 SDK
            DeviceStore.shared.openLocalCamera(isFront: isFront) { result in
                switch result {
                case .success:
                    print("[DeviceManager] 摄像头打开成功, 前置: \(isFront)")
                    completion(.success(()))
                case .failure(let error):
                    print("[DeviceManager] 摄像头打开失败, code: \(error.code)")
                    completion(.failure(error))
                }
            }
        }
    }

    /// 关闭本地摄像头
    func closeCamera() {
        DeviceStore.shared.closeLocalCamera()
        print("[DeviceManager] 摄像头已关闭")
    }

    /// 切换前后摄像头（不中断推流）
    func switchCamera(toFront: Bool) {
        DeviceStore.shared.switchCamera(isFront: toFront)
        print("[DeviceManager] 摄像头已切换至: \(toFront ? "前置" : "后置")")
    }

    // MARK: - 麦克风操作

    /// 打开本地麦克风（含权限检查）
    func openMicrophone(completion: @escaping (Result<Void, Error>) -> Void) {
        checkMicrophonePermission { [weak self] granted in
            guard granted else {
                completion(.failure(DevicePermissionError.microphoneNotAuthorized))
                return
            }
            DeviceStore.shared.openLocalMicrophone { result in
                switch result {
                case .success:
                    print("[DeviceManager] 麦克风打开成功")
                    completion(.success(()))
                case .failure(let error):
                    print("[DeviceManager] 麦克风打开失败, code: \(error.code)")
                    completion(.failure(error))
                }
            }
        }
    }

    /// 关闭本地麦克风
    func closeMicrophone() {
        DeviceStore.shared.closeLocalMicrophone()
        print("[DeviceManager] 麦克风已关闭")
    }

    // MARK: - 批量操作（主播场景）

    /// 主播开播：同时打开摄像头和麦克风
    func openAllDevicesForAnchor(completion: @escaping (Result<Void, Error>) -> Void) {
        openCamera(isFront: true) { [weak self] cameraResult in
            guard let self = self else { return }
            switch cameraResult {
            case .failure(let error):
                completion(.failure(error))
            case .success:
                self.openMicrophone { micResult in
                    completion(micResult)
                }
            }
        }
    }

    /// 主播下播：关闭所有设备
    func closeAllDevices() {
        closeCamera()
        closeMicrophone()
    }
}

// MARK: - 权限错误类型

enum DevicePermissionError: LocalizedError {
    case cameraNotAuthorized
    case microphoneNotAuthorized

    var errorDescription: String? {
        switch self {
        case .cameraNotAuthorized:
            return "摄像头权限未授予，请前往「设置 > 隐私 > 摄像头」开启"
        case .microphoneNotAuthorized:
            return "麦克风权限未授予，请前往「设置 > 隐私 > 麦克风」开启"
        }
    }
}
```

**使用示例（主播开播）**：
```swift
func startBroadcast() {
    DeviceManager.shared.openAllDevicesForAnchor { result in
        switch result {
        case .success:
            // 设备就绪，可以进房推流
            self.enterLiveRoom()
        case .failure(let error):
            if let permError = error as? DevicePermissionError {
                // 引导用户去系统设置开启权限
                self.showPermissionGuideAlert(message: permError.localizedDescription)
            } else {
                self.showAlert(message: error.localizedDescription)
            }
        }
    }
}

// 主播下播
func stopBroadcast() {
    DeviceManager.shared.closeAllDevices()
    exitLiveRoom()
}
```

## 调用时序

```
权限检查
    │
    ├─ 未确定（notDetermined）
    │       └─ 系统弹窗 → 用户授权/拒绝
    │
    ├─ 已拒绝（denied）
    │       └─ 展示引导弹窗 → 跳转系统设置
    │
    └─ 已授权（authorized）
            │
            ▼
    DeviceStore.openLocalCamera(isFront: true)
            │
            ├─ .failure(error)
            │       ├─ -1100 重试或上报
            │       ├─ -1101 系统授权异常（重新检查）
            │       ├─ -1102 提示关闭其他应用
            │       └─ -1103 模拟器，提示换真机
            │
            └─ .success
                    │
                    ▼
            DeviceStore.openLocalMicrophone()
                    │
                    ├─ .failure(error) → 同上处理
                    │
                    └─ .success
                            │
                            ▼
                    设备就绪，进行推流/预览
                            │
                    [使用中]
                            │
                            ▼
                    DeviceStore.closeLocalCamera()
                    DeviceStore.closeLocalMicrophone()
                    （下播 / 退房 / App 进入后台）
```

## 平台特有注意事项

### 1. iOS 权限弹窗时机
系统权限弹窗**只会弹出一次**（首次请求时）。若用户拒绝后，后续调用 `requestAccess` 不再弹窗，必须引导用户手动前往系统设置开启。建议在开播前明确告知用户权限用途，提高授权通过率。

### 2. 后台摄像头自动关闭
iOS 系统在 App 进入后台时会**自动挂起摄像头采集**。主播场景中若需要后台推流，须在 `Info.plist` 中开启后台音视频模式：
```xml
<key>UIBackgroundModes</key>
<array>
    <string>audio</string>
</array>
```
即使开启后台模式，摄像头视频帧在后台仍会停止推送，建议切后台时向观众提示"主播暂时离开"。

### 3. 摄像头被其他进程占用（-1102）
iOS 系统级应用（如 FaceTime、系统相机）在前台时会独占摄像头。当 App 从后台切回前台并重新打开摄像头时，若系统摄像头仍被其他应用持有，会触发 `-1102`。解决方案：监听 `UIApplication.didBecomeActiveNotification`，延迟 0.5~1 秒后重试打开摄像头。
