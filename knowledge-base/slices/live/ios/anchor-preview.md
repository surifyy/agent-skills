---
id: live/anchor-preview
platform: ios
---

# 主播预览 — iOS 实现

## 前置条件

**依赖安装（Podfile）**
```ruby
pod 'AtomicXCore', '~> 4.0'
```

**Info.plist 权限声明**
```xml
<key>NSCameraUsageDescription</key>
<string>需要访问摄像头以进行视频直播</string>
<key>NSMicrophoneUsageDescription</key>
<string>需要访问麦克风以进行语音直播</string>
```

**前置状态**：
- `LoginStore.shared.isLogin == true`（须完成登录）
- 摄像头/麦克风系统权限已授予
- 已有合法的 `liveID`（ASCII 字符，长度 ≤ 48 字节）

## API 调用

```swift
// 1. 创建推流视图
let pushView = LiveCoreView(viewType: .pushView)

// 2. 绑定直播间 ID（必须在 openLocalCamera 之前调用）
pushView.setLiveID(liveID)

// 3. 打开前置摄像头
DeviceStore.shared.openLocalCamera(
    isFront: true,
    completion: ((Result<Void, DeviceError>) -> Void)?
)

// 4. 打开麦克风
DeviceStore.shared.openLocalMicrophone(
    completion: ((Result<Void, DeviceError>) -> Void)?
)

// 5. 退出预览时关闭设备
DeviceStore.shared.closeLocalCamera()
DeviceStore.shared.closeLocalMicrophone()
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `viewType` | `LiveCoreViewType` | `.pushView` = 主播推流预览；`.playView` = 观众拉流播放 |
| `isFront` | `Bool` | `true` = 前置摄像头（默认），`false` = 后置 |
| `completion` | `Result<Void, DeviceError>?` | 主线程回调；`nil` 表示不关心结果 |

## 代码示例

```swift
import UIKit
import AtomicXCore
import AVFoundation
import Combine

/// 主播预览页面
final class AnchorPreviewViewController: UIViewController {

    // MARK: - Properties

    private let liveID: String
    private var pushView: LiveCoreView!
    private var cancellables = Set<AnyCancellable>()

    // MARK: - Init

    init(liveID: String) {
        self.liveID = liveID
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) { fatalError() }

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupPreview()
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        // 退出预览时释放设备
        teardownPreview()
    }

    // MARK: - UI Setup

    private func setupUI() {
        view.backgroundColor = .black

        // 创建推流视图
        pushView = LiveCoreView(viewType: .pushView)
        pushView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(pushView)

        NSLayoutConstraint.activate([
            pushView.topAnchor.constraint(equalTo: view.topAnchor),
            pushView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            pushView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            pushView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])

        // 开播按钮
        let startButton = UIButton(type: .system)
        startButton.setTitle("开始直播", for: .normal)
        startButton.titleLabel?.font = .systemFont(ofSize: 18, weight: .semibold)
        startButton.backgroundColor = UIColor.systemRed
        startButton.setTitleColor(.white, for: .normal)
        startButton.layer.cornerRadius = 24
        startButton.translatesAutoresizingMaskIntoConstraints = false
        startButton.addTarget(self, action: #selector(startLiveTapped), for: .touchUpInside)
        view.addSubview(startButton)

        NSLayoutConstraint.activate([
            startButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            startButton.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -32),
            startButton.widthAnchor.constraint(equalToConstant: 200),
            startButton.heightAnchor.constraint(equalToConstant: 48)
        ])
    }

    // MARK: - Preview Setup

    private func setupPreview() {
        // 步骤 1：绑定 liveID（必须在 openLocalCamera 之前）
        pushView.setLiveID(liveID)

        // 步骤 2：检查并请求摄像头权限
        checkCameraPermission { [weak self] granted in
            guard let self else { return }
            guard granted else {
                self.showPermissionAlert(for: .video)
                return
            }
            self.openCameraAndMic()
        }
    }

    private func openCameraAndMic() {
        // 步骤 3：打开前置摄像头
        DeviceStore.shared.openLocalCamera(isFront: true) { [weak self] result in
            guard let self else { return }
            switch result {
            case .success:
                print("[AnchorPreview] 摄像头打开成功")
                // 步骤 4：打开麦克风
                self.openMicrophone()
            case .failure(let error):
                print("[AnchorPreview] 摄像头打开失败 code: \(error.code)")
                self.handleDeviceError(error)
            }
        }
    }

    private func openMicrophone() {
        DeviceStore.shared.openLocalMicrophone { [weak self] result in
            switch result {
            case .success:
                print("[AnchorPreview] 麦克风打开成功，预览就绪")
            case .failure(let error):
                print("[AnchorPreview] 麦克风打开失败 code: \(error.code)")
                self?.handleDeviceError(error)
            }
        }
    }

    private func teardownPreview() {
        DeviceStore.shared.closeLocalCamera()
        DeviceStore.shared.closeLocalMicrophone()
    }

    // MARK: - Actions

    @objc private func startLiveTapped() {
        // 导航至房间配置页面，再由配置页面调用 createLive
        let configVC = AnchorRoomConfigViewController(liveID: liveID)
        navigationController?.pushViewController(configVC, animated: true)
    }

    // MARK: - Permission Helpers

    private func checkCameraPermission(completion: @escaping (Bool) -> Void) {
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

    private func showPermissionAlert(for mediaType: AVMediaType) {
        let message = mediaType == .video
            ? "请在「设置 > 隐私 > 摄像头」中允许本应用访问摄像头"
            : "请在「设置 > 隐私 > 麦克风」中允许本应用访问麦克风"
        let alert = UIAlertController(title: "权限不足", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "去设置", style: .default) { _ in
            if let url = URL(string: UIApplication.openSettingsURLString) {
                UIApplication.shared.open(url)
            }
        })
        alert.addAction(UIAlertAction(title: "取消", style: .cancel))
        present(alert, animated: true)
    }

    private func handleDeviceError(_ error: DeviceError) {
        let message: String
        switch error.code {
        case -1101: message = "摄像头权限被拒，请前往系统设置开启"
        case -1102: message = "摄像头被其他应用占用，请关闭后重试"
        case -1103: message = "当前设备不支持摄像头（请使用真机测试）"
        case -1105: message = "麦克风权限被拒，请前往系统设置开启"
        default:    message = "设备打开失败（错误码 \(error.code)），请重试"
        }
        let alert = UIAlertController(title: "设备错误", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default))
        present(alert, animated: true)
    }
}
```

## 调用时序

```
AnchorPreviewViewController.viewDidLoad()
        │
        ▼
pushView = LiveCoreView(viewType: .pushView)
        │
        ▼
view.addSubview(pushView)               ← 先加入视图层级
        │
        ▼
pushView.setLiveID(liveID)              ← 绑定直播间 ID（不可跳过！）
        │
        ▼
checkCameraPermission()
        │
        ├─ denied  → showPermissionAlert → 用户跳转系统设置
        │
        └─ authorized
                │
                ▼
        DeviceStore.openLocalCamera(isFront: true)
                │
                ├─ .failure → handleDeviceError（显示错误提示）
                │
                └─ .success
                        │
                        ▼
                DeviceStore.openLocalMicrophone()
                        │
                        └─ .success → 预览画面出现，等待用户点击「开始直播」
                                │
                                ▼
                        [用户点击开始直播]
                                │
                                ▼
                        导航到 AnchorRoomConfigViewController
                        （由配置页面调用 createLive）
        │
viewWillDisappear()
        │
        ▼
DeviceStore.closeLocalCamera()
DeviceStore.closeLocalMicrophone()      ← 退出预览时释放设备
```

## 平台特有注意事项

### 1. setLiveID 必须在 addSubview 之后调用
`LiveCoreView` 内部渲染管道在加入视图层级后才完整初始化。若在 `addSubview` 之前调用 `setLiveID`，可能导致渲染通道绑定失败，表现为黑屏。

### 2. iOS 模拟器不支持摄像头
所有摄像头相关功能必须在**真实设备**上测试。模拟器调用 `openLocalCamera` 会返回 `-1103`。

### 3. 进入后台时摄像头自动暂停
iOS 系统在 App 进入后台时会自动挂起摄像头采集。监听 `UIApplication.didEnterBackgroundNotification` 主动关闭设备，再在 `didBecomeActiveNotification` 时重新打开，避免 `-1102` 被占用错误：

```swift
NotificationCenter.default.publisher(for: UIApplication.didEnterBackgroundNotification)
    .sink { [weak self] _ in self?.teardownPreview() }
    .store(in: &cancellables)

NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)
    .sink { [weak self] _ in self?.openCameraAndMic() }
    .store(in: &cancellables)
```

### 4. 前后摄像头切换（不中断预览）
预览阶段可直接调用 `DeviceStore.shared.switchCamera(isFront:)` 切换前后摄像头，无需重新调用 `openLocalCamera`，画面切换无黑屏。
