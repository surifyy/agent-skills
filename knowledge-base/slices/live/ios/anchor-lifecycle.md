---
id: live/anchor-lifecycle
platform: ios
---

# 主播开播与结束生命周期 — iOS 实现

## 前置条件

**依赖安装（Podfile）**
```ruby
pod 'AtomicXCore', '~> 4.0'
```

**前置状态**：
- `LoginStore.shared.isLogin == true`（须完成登录）
- `DeviceStore.shared.openLocalCamera` 已成功（摄像头就绪）
- `DeviceStore.shared.openLocalMicrophone` 已成功（麦克风就绪）
- `LiveInfo` 已配置完毕（liveID + seatTemplate 必填）

## API 调用

```swift
// 开播
LiveListStore.shared.createLive(liveInfo: liveInfo) { result in
    // result: Result<Void, LiveError>
}

// 结束直播
LiveListStore.shared.endLive(liveID: liveID) { result in
    // result: Result<Void, LiveError>
}

// 订阅被动结束事件（Combine）
LiveListStore.liveListEventPublisher
    .receive(on: DispatchQueue.main)
    .sink { event in
        switch event {
        case .onLiveEnded(let liveID):       // 直播被动结束
        case .onKickedOutOfLive(let liveID, let reason):  // 被踢出直播间
        default: break
        }
    }
    .store(in: &cancellables)
```

## 代码示例

### 开播代码

```swift
import UIKit
import AtomicXCore
import Combine

/// 直播中页面 — 完整生命周期管理
final class AnchorLiveViewController: UIViewController {

    // MARK: - Properties

    private let liveID: String
    private var cancellables = Set<AnyCancellable>()
    private var isLiving = false

    // MARK: - UI

    private lazy var endButton: UIButton = {
        let btn = UIButton(type: .system)
        btn.setTitle("结束直播", for: .normal)
        btn.backgroundColor = .systemRed
        btn.setTitleColor(.white, for: .normal)
        btn.layer.cornerRadius = 20
        btn.addTarget(self, action: #selector(endLiveTapped), for: .touchUpInside)
        return btn
    }()

    private let statusLabel: UILabel = {
        let label = UILabel()
        label.text = "正在开播中…"
        label.textColor = .white
        label.font = .systemFont(ofSize: 14)
        return label
    }()

    // MARK: - Init

    init(liveID: String) {
        self.liveID = liveID
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) { fatalError() }

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .black
        setupLayout()
        subscribeToLiveEvents()
        startLive()
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        // 防止导航返回时未调用 endLive
        if isLiving {
            performEndLive()
        }
    }

    // MARK: - Layout

    private func setupLayout() {
        [statusLabel, endButton].forEach {
            $0.translatesAutoresizingMaskIntoConstraints = false
            view.addSubview($0)
        }
        NSLayoutConstraint.activate([
            statusLabel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 16),
            statusLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),

            endButton.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -32),
            endButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            endButton.widthAnchor.constraint(equalToConstant: 160),
            endButton.heightAnchor.constraint(equalToConstant: 40)
        ])
    }

    // MARK: - Start Live

    private func startLive() {
        var liveInfo = LiveInfo()
        liveInfo.liveID       = liveID
        liveInfo.liveName     = "我的直播间"
        liveInfo.seatTemplate = .videoDynamicGrid9Seats

        LiveListStore.shared.createLive(liveInfo: liveInfo) { [weak self] result in
            guard let self else { return }
            DispatchQueue.main.async {
                switch result {
                case .success:
                    self.isLiving = true
                    self.statusLabel.text = "🔴 直播中"
                    print("[AnchorLive] 开播成功, liveID: \(self.liveID)")

                case .failure(let error):
                    self.handleCreateError(error)
                }
            }
        }
    }

    // MARK: - Event Subscription

    private func subscribeToLiveEvents() {
        LiveListStore.liveListEventPublisher
            .receive(on: DispatchQueue.main)
            .sink { [weak self] event in
                guard let self else { return }
                switch event {
                case .onLiveEnded(let endedLiveID) where endedLiveID == self.liveID:
                    // 直播被服务端强制结束（如违规、服务端超时等）
                    print("[AnchorLive] 直播被动结束, liveID: \(endedLiveID)")
                    self.handleLivePassiveEnd(reason: "直播已被系统结束")

                case .onKickedOutOfLive(let kickedLiveID, let reason) where kickedLiveID == self.liveID:
                    // 主播被管理员踢出
                    print("[AnchorLive] 被踢出直播间, reason: \(reason)")
                    self.handleKickedOut(reason: reason)

                default:
                    break
                }
            }
            .store(in: &cancellables)
    }

    // MARK: - End Live

    @objc private func endLiveTapped() {
        let alert = UIAlertController(title: "确认结束直播", message: "观众将无法继续观看，是否确认？",
                                      preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "结束直播", style: .destructive) { [weak self] _ in
            self?.performEndLive()
        })
        alert.addAction(UIAlertAction(title: "取消", style: .cancel))
        present(alert, animated: true)
    }

    private func performEndLive() {
        guard isLiving else { return }
        isLiving = false

        endButton.isEnabled = false
        statusLabel.text = "直播结束中…"

        // 步骤 1：结束 PK（如有）
        // endPK { ... }

        // 步骤 2：断开连线（如有）
        // disconnectLink { ... }

        // 步骤 3：断开连麦（如有）
        // stopCoguest { ... }

        // 步骤 4：关闭设备
        DeviceStore.shared.closeLocalCamera()
        DeviceStore.shared.closeLocalMicrophone()

        // 步骤 5：结束直播
        LiveListStore.shared.endLive(liveID: liveID) { [weak self] result in
            guard let self else { return }
            DispatchQueue.main.async {
                switch result {
                case .success:
                    print("[AnchorLive] 直播结束成功")
                    // 步骤 6：endLive 回调成功后才可释放资源
                    self.cleanupAndDismiss()

                case .failure(let error):
                    print("[AnchorLive] endLive 失败, code: \(error.code)")
                    // 即使失败也应清理本地资源
                    self.cleanupAndDismiss()
                }
            }
        }
    }

    // MARK: - Passive End Handlers

    private func handleLivePassiveEnd(reason: String) {
        isLiving = false
        DeviceStore.shared.closeLocalCamera()
        DeviceStore.shared.closeLocalMicrophone()

        let alert = UIAlertController(title: "直播已结束", message: reason, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default) { [weak self] _ in
            self?.cleanupAndDismiss()
        })
        present(alert, animated: true)
    }

    private func handleKickedOut(reason: String) {
        isLiving = false
        DeviceStore.shared.closeLocalCamera()
        DeviceStore.shared.closeLocalMicrophone()

        let message = reason.isEmpty ? "您已被管理员移出直播间" : "被移出原因：\(reason)"
        let alert = UIAlertController(title: "已被移出", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default) { [weak self] _ in
            self?.cleanupAndDismiss()
        })
        present(alert, animated: true)
    }

    // MARK: - Cleanup

    private func cleanupAndDismiss() {
        // 取消所有事件订阅
        cancellables.removeAll()
        // 返回上层（此时 LiveCoreView 已安全释放）
        navigationController?.popToRootViewController(animated: true)
    }

    // MARK: - Error Handling

    private func handleCreateError(_ error: LiveError) {
        let message: String
        switch error.code {
        case -2105: message = "直播间 ID 格式非法"
        case -2107: message = "直播间名称非法（超长或含特殊字符）"
        case -2108: message = "您已在其他直播间，请先退出"
        default:    message = "开播失败（错误码 \(error.code)）"
        }
        let alert = UIAlertController(title: "开播失败", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default) { [weak self] _ in
            self?.navigationController?.popViewController(animated: true)
        })
        present(alert, animated: true)
    }
}
```

## 调用时序

```
AnchorLiveViewController.viewDidLoad()
        │
        ├─── subscribeToLiveEvents()       ← 先订阅事件，防止 createLive 成功前的事件丢失
        │
        └─── startLive()
                │
                ▼
        LiveInfo 构建
        （liveID + liveName + seatTemplate）
                │
                ▼
        LiveListStore.createLive(liveInfo:)
                │
                ├─ .failure(-2105/-2107/-2108) → 展示错误弹窗，返回上页
                │
                └─ .success
                        │
                        ▼
                isLiving = true
                UI 更新为「🔴 直播中」
                        │
                        ▼
                ┌───────────────────────────┐
                │       直播进行中          │
                │   事件监听持续运行中      │
                │   onLiveEnded → 被动结束  │
                │   onKickedOutOfLive → 踢出│
                └───────────────────────────┘
                        │
                [用户点击「结束直播」/ 被动结束]
                        │
                        ▼
        步骤1: endPK()（如有）
        步骤2: disconnectLink()（如有）
        步骤3: stopCoguest()（如有）
        步骤4: DeviceStore.closeLocalCamera()
               DeviceStore.closeLocalMicrophone()
        步骤5: LiveListStore.endLive(liveID:)
                │
                └─ .success / .failure
                        │
                        ▼
        步骤6: cancellables.removeAll()    ← 取消事件订阅
               navigationController?.popToRootViewController()
               （此时 LiveCoreView 安全释放）
```

## 平台特有注意事项

### 1. Combine 订阅生命周期管理
`liveListEventPublisher` 的 Combine 订阅存储在 `cancellables` 中。务必在 `cleanupAndDismiss` 时调用 `cancellables.removeAll()`，否则：
- ViewController 被释放后订阅仍存活（内存泄漏）
- 后续事件可能触发已释放对象的回调（野指针）

### 2. App 进入后台时的处理
iOS 系统在 App 后台时可能中断网络连接，导致推流断开。建议监听 App 生命周期：

```swift
NotificationCenter.default.publisher(for: UIApplication.willResignActiveNotification)
    .sink { [weak self] _ in
        // 可在此展示「主播暂时离开」提示给观众
        print("[AnchorLive] App 进入后台，推流可能中断")
    }
    .store(in: &cancellables)
```

### 3. endLive 失败时的兜底处理
网络异常可能导致 `endLive` 回调超时或失败。即使失败也应清理本地资源（关闭设备、取消订阅），并在下次启动时通过服务端状态检查直播间是否仍存在。

### 4. 导航返回的拦截
使用 `viewWillDisappear` 中的 `isLiving` 标志检测用户通过导航返回键意外退出直播间，确保 `endLive` 被调用：

```swift
override func viewWillDisappear(_ animated: Bool) {
    super.viewWillDisappear(animated)
    if isLiving && isMovingFromParent {
        performEndLive()
    }
}
```
