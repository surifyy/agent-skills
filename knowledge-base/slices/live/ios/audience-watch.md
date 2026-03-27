---
id: live/audience-watch
platform: ios
---

# 观众观看 — iOS 实现

## 前置条件

**依赖安装（Podfile）**
```ruby
pod 'AtomicXCore', '~> 4.0'
```

**最低系统要求**：iOS 13.0+，Xcode 14.0+

**前置登录**：必须在 `LoginStore.shared.login` 成功后才可调用 `joinLive`。

**权限说明**：观众使用 `.playView` 仅拉流，**无需**申请摄像头/麦克风权限。若观众发起连麦则需相机与麦克风权限（参见 live/device-control）。

## API 调用

```swift
// 获取播放视图（添加到视图层级）
liveCoreView.getView(type: .playView) -> UIView

// 绑定目标直播间（joinLive 之前必须调用）
liveCoreView.setLiveID(_ liveID: String)

// 进入直播间并开始拉流
liveCoreView.joinLive(
    completion: ((Result<Void, Error>) -> Void)?
)

// 退出直播间并释放媒体资源
liveCoreView.leaveLive(
    completion: ((Result<Void, Error>) -> Void)?
)

// 订阅直播事件（Combine）
LiveListStore.shared.liveListEventPublisher: AnyPublisher<LiveListEvent, Never>
// 关注：.onKickedOutOfLive(liveID:)
```

## 代码示例

### 完整进房流程

```swift
import AtomicXCore
import Combine
import UIKit

final class AudienceWatchViewController: UIViewController {

    // MARK: - Properties

    private let liveID: String
    private let liveCoreView = LiveCoreView()
    private var cancellables = Set<AnyCancellable>()
    private var isInLive = false        // 标记是否已成功进房
    private var isConnecting = false    // 标记是否处于连麦状态

    // MARK: - Init

    init(liveID: String) {
        self.liveID = liveID
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) { fatalError() }

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        setupPlayView()
        subscribeEvents()
        enterLive()
    }

    override func viewDidDisappear(_ animated: Bool) {
        super.viewDidDisappear(animated)
        // 页面消失时确保退出直播间
        exitLive()
    }

    // MARK: - Setup

    private func setupPlayView() {
        view.backgroundColor = .black

        // Step 1: 获取 playView 并添加到视图层级
        let playView = liveCoreView.getView(type: .playView)
        view.addSubview(playView)
        playView.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            playView.topAnchor.constraint(equalTo: view.topAnchor),
            playView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            playView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            playView.trailingAnchor.constraint(equalTo: view.trailingAnchor)
        ])
    }

    // MARK: - 订阅事件

    private func subscribeEvents() {
        LiveListStore.shared.liveListEventPublisher
            .receive(on: DispatchQueue.main)
            .sink { [weak self] event in
                switch event {
                case .onKickedOutOfLive(let liveID):
                    // 只处理当前直播间的踢出事件
                    guard liveID == self?.liveID else { return }
                    self?.handleKickedOut()
                case .onLiveEnded(let liveID):
                    guard liveID == self?.liveID else { return }
                    self?.handleLiveEnded()
                }
            }
            .store(in: &cancellables)
    }

    // MARK: - 进房

    private func enterLive() {
        // Step 2: 必须先 setLiveID，再 joinLive
        liveCoreView.setLiveID(liveID)

        // Step 3: 进入直播间
        liveCoreView.joinLive { [weak self] result in
            DispatchQueue.main.async {
                guard let self = self else { return }
                switch result {
                case .success:
                    self.isInLive = true
                    print("[AudienceWatch] 进房成功: \(self.liveID)")
                    // Step 4: 进房成功后再启用弹幕/礼物等功能
                    self.enableInteractiveFeatures()
                case .failure(let error):
                    print("[AudienceWatch] 进房失败: \(error)")
                    self.showEnterFailedAlert(error: error)
                }
            }
        }
    }

    // MARK: - 退出

    private func exitLive() {
        guard isInLive else { return }

        if isConnecting {
            // 连麦状态下：先断开连麦，再退出直播间
            disconnectMic { [weak self] in
                self?.performLeaveLive()
            }
        } else {
            performLeaveLive()
        }
    }

    private func disconnectMic(completion: @escaping () -> Void) {
        // 断开连麦（具体 API 参见 live/audience-link-mic）
        // liveCoreView.disConnect { _ in completion() }
        completion()  // 占位，替换为真实连麦断开接口
    }

    private func performLeaveLive() {
        isInLive = false
        liveCoreView.leaveLive { result in
            switch result {
            case .success:
                print("[AudienceWatch] 退出直播间成功")
            case .failure(let error):
                print("[AudienceWatch] 退出直播间失败: \(error)")
                // 即使失败也清理本地状态，避免残留
            }
        }
    }

    // MARK: - 事件处理

    private func handleKickedOut() {
        isInLive = false
        showToast("您已被移出直播间")
        navigationController?.popViewController(animated: true)
    }

    private func handleLiveEnded() {
        isInLive = false
        showToast("直播已结束")
        navigationController?.popViewController(animated: true)
    }

    // MARK: - 功能启用（进房成功后调用）

    private func enableInteractiveFeatures() {
        // 在此初始化弹幕、礼物、连麦申请等组件
    }

    // MARK: - UI Helpers

    private func showEnterFailedAlert(error: Error) {
        let alert = UIAlertController(
            title: "进入直播间失败",
            message: error.localizedDescription,
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "返回", style: .default) { [weak self] _ in
            self?.navigationController?.popViewController(animated: true)
        })
        present(alert, animated: true)
    }

    private func showToast(_ message: String) {
        // 展示轻提示（业务自行实现）
        print("[Toast] \(message)")
    }
}
```

### App 生命周期处理

```swift
// 在 AppDelegate 或 SceneDelegate 中注册，或在 ViewController 的 viewWillAppear 中注册

// 进入后台：停止拉流，避免后台占用解码资源
NotificationCenter.default.addObserver(
    forName: UIApplication.didEnterBackgroundNotification,
    object: nil,
    queue: .main
) { [weak self] _ in
    // 观众后台时停播（不退房）；需要时可在前台恢复继续播放
    // 若业务要求后台不能播放，则调用 leaveLive 并在前台时重新 joinLive
}

// 回到前台：恢复播放
NotificationCenter.default.addObserver(
    forName: UIApplication.willEnterForegroundNotification,
    object: nil,
    queue: .main
) { [weak self] _ in
    // 如已调用 leaveLive，需重新 setLiveID + joinLive
    // 如未退房（仅暂停），可直接恢复播放
}
```

## 调用时序

```
LoginStore.login 成功
    │
    ▼
AudienceWatchViewController.viewDidLoad
    │
    ├─ setupPlayView：getView(.playView) → addSubview
    ├─ subscribeEvents：订阅 onKickedOutOfLive / onLiveEnded
    │
    ▼
liveCoreView.setLiveID(liveID)      ← 必须在 joinLive 之前
    │
    ▼
liveCoreView.joinLive
    │
    ├─ .failure
    │       ├─ -1002 → 先登录
    │       ├─ -2001 → 直播已结束 → popViewController
    │       └─ 其他  → showAlert
    │
    └─ .success → isInLive = true → 启用弹幕/礼物功能
            │
            ▼
        用户退出 / 收到 onKickedOutOfLive / onLiveEnded
            │
            ├─ 连麦中？ → disConnect → leaveLive
            └─ 未连麦  → leaveLive
```

## 平台特有注意事项

### 1. viewDidDisappear vs deinit 中调用 leaveLive

建议在 `viewDidDisappear` 中调用而非 `deinit`，原因：iOS push/pop 导航栈时，上级页面不会被销毁（`deinit` 不调用），但 `viewDidDisappear` 会触发。如在 `deinit` 中释放，可能导致用户返回列表后资源未释放直到页面从栈中弹出。

### 2. 强引用导致 LiveCoreView 无法释放

若闭包中捕获 `self` 导致循环引用，`leaveLive` 的回调永远不执行。始终使用 `[weak self]` 捕获 ViewController 引用。

### 3. 横竖屏切换时 playView 的 frame 更新

`LiveCoreView.getView(type:)` 返回的 UIView 不会自动响应设备旋转，需在 `viewDidLayoutSubviews` 中更新 `playView.frame` 或使用 AutoLayout 约束（推荐）。

### 4. 后台播放与 App Store 合规

若 App 允许后台音频播放，需在 `Info.plist` 的 `UIBackgroundModes` 中声明 `audio`，否则 App 进入后台后音频会被系统静音，且审核可能被拒。若不支持后台播放，进后台时调用 `leaveLive` 是更安全的选择。
