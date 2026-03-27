---
id: live/gift
platform: ios
---

# 礼物 — iOS 实现

## 前置条件

**依赖安装（Podfile）**
```ruby
pod 'AtomicXCore', '~> 4.0'
```

**前置状态**：
- `LoginStore.shared.isLogin == true`（礼物功能依赖登录态）
- 已成功加入直播间（liveID 与进房 ID 一致）
- 服务端已配置礼物系统及扣费回调

## API 调用

```swift
// 创建礼物实例（与直播间绑定）
let giftStore = GiftStore.create(liveID: liveID)

// （可选）设置语言，须在 refreshUsableGifts 前调用
giftStore.setLanguage("zh-CN")

// 拉取礼物列表
giftStore.refreshUsableGifts(completion: ((Result<Void, Error>) -> Void)?)

// 发送礼物
giftStore.sendGift(
    giftID: String,
    count: UInt,
    completion: ((Result<Void, Error>) -> Void)?
)

// 订阅礼物事件
giftStore.giftEventPublisher
    .sink { event in
        switch event {
        case .onReceiveGift(let giftInfo):
            // 处理礼物动画
        }
    }
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `liveID` | `String` | 直播间唯一标识 |
| `giftID` | `String` | 礼物唯一 ID，来自 `GiftState.usableGifts` |
| `count` | `UInt` | 发送数量，最小为 1 |

## 代码示例

### 完整礼物集成

```swift
import AtomicXCore
import Combine

final class GiftManager {

    // MARK: - 属性

    private let giftStore: GiftStore
    private var cancellables = Set<AnyCancellable>()

    /// 礼物分类列表（供 UI 面板使用）
    @Published private(set) var giftCategories: [GiftCategory] = []

    // MARK: - 初始化

    init(liveID: String, language: String = "zh-CN") {
        // 步骤1: 创建 GiftStore 实例
        self.giftStore = GiftStore.create(liveID: liveID)

        // 步骤2: 多语言场景先设置语言
        giftStore.setLanguage(language)

        // 步骤3: 订阅礼物事件（进房后立即订阅，避免遗漏）
        subscribeGiftEvents()

        // 步骤4: 订阅礼物列表状态
        subscribeGiftState()
    }

    // MARK: - 礼物列表

    /// 拉取可用礼物列表（面板打开前调用）
    func loadGifts(completion: ((Result<Void, Error>) -> Void)? = nil) {
        giftStore.refreshUsableGifts { result in
            switch result {
            case .success:
                print("[Gift] 礼物列表拉取成功")
                completion?(.success(()))
            case .failure(let error):
                print("[Gift] 礼物列表拉取失败: \(error)")
                completion?(.failure(error))
            }
        }
    }

    private func subscribeGiftState() {
        giftStore.$state
            .map(\.usableGifts)
            .receive(on: DispatchQueue.main)
            .assign(to: &$giftCategories)
    }

    // MARK: - 礼物事件订阅

    private func subscribeGiftEvents() {
        // 步骤5: 通过 giftEventPublisher 处理所有礼物 UI
        giftStore.giftEventPublisher
            .receive(on: DispatchQueue.main)
            .sink { [weak self] event in
                switch event {
                case .onReceiveGift(let giftInfo):
                    self?.handleReceiveGift(giftInfo)
                }
            }
            .store(in: &cancellables)
    }

    private func handleReceiveGift(_ giftInfo: GiftReceiveInfo) {
        print("[Gift] 收到礼物: \(giftInfo.gift.name) ×\(giftInfo.count) from \(giftInfo.senderID)")

        // 播放礼物动画
        GiftAnimationPlayer.shared.play(
            resourceURL: giftInfo.gift.resourceURL,
            senderName: giftInfo.senderName,
            giftName: giftInfo.gift.name,
            count: giftInfo.count
        )

        // 在弹幕区插入礼物通知（通过 BarrageStore.appendLocalTip）
        // 见 live/barrage slice
    }

    // MARK: - 发送礼物

    /// 发送礼物（从礼物面板调用）
    func sendGift(giftID: String,
                  count: UInt = 1,
                  completion: ((Result<Void, Error>) -> Void)? = nil) {
        // 步骤6: 发送礼物
        giftStore.sendGift(giftID: giftID, count: count) { result in
            switch result {
            case .success:
                // ✅ 成功后不在此处展示动画！
                // 动画由 giftEventPublisher 统一驱动（发送方也会收到 onReceiveGift）
                completion?(.success(()))

            case .failure(let error):
                // ❌ 仅在失败时处理
                print("[Gift] 发送失败: \(error)")
                completion?(.failure(error))
            }
        }
    }

    // MARK: - 资源清理

    func cleanup() {
        cancellables.removeAll()
    }
}
```

### 礼物面板 ViewController

```swift
final class GiftPanelViewController: UIViewController {

    private var giftManager: GiftManager!
    private var cancellables = Set<AnyCancellable>()

    // 面板 CollectionView（展示礼物分类 + 礼物列表）
    @IBOutlet weak var collectionView: UICollectionView!
    @IBOutlet weak var loadingIndicator: UIActivityIndicatorView!

    override func viewDidLoad() {
        super.viewDidLoad()

        // 绑定礼物列表数据
        giftManager.$giftCategories
            .receive(on: DispatchQueue.main)
            .sink { [weak self] categories in
                guard !categories.isEmpty else { return }
                self?.collectionView.reloadData()
                self?.loadingIndicator.stopAnimating()
            }
            .store(in: &cancellables)

        // 步骤: 面板出现时拉取礼物列表
        loadingIndicator.startAnimating()
        giftManager.loadGifts { [weak self] result in
            if case .failure(let error) = result {
                self?.showError(error)
                self?.loadingIndicator.stopAnimating()
            }
        }
    }

    // 用户点击礼物
    func didSelectGift(_ gift: Gift, count: UInt) {
        giftManager.sendGift(giftID: gift.giftID, count: count) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success:
                    break // 动画由 giftEventPublisher 驱动，此处无需操作
                case .failure(let error):
                    self?.handleSendError(error)
                }
            }
        }
    }

    private func handleSendError(_ error: Error) {
        let code = (error as? GiftError)?.code ?? -1
        switch code {
        case -4001:
            showRechargeAlert()   // 余额不足，引导充值
        case -4002:
            // 礼物不存在，刷新列表
            giftManager.loadGifts()
        default:
            showErrorToast(message: error.localizedDescription)
        }
    }

    private func showRechargeAlert() {
        let alert = UIAlertController(
            title: "余额不足",
            message: "当前金币不足，是否前往充值？",
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "去充值", style: .default) { _ in
            // 跳转充值页面
        })
        alert.addAction(UIAlertAction(title: "取消", style: .cancel))
        present(alert, animated: true)
    }
}
```

### 多语言礼物列表

```swift
// 根据系统语言自动选择
func makeGiftManager(liveID: String) -> GiftManager {
    let languageCode: String
    if let preferred = Locale.preferredLanguages.first {
        languageCode = preferred.hasPrefix("zh") ? "zh-CN" : "en"
    } else {
        languageCode = "zh-CN"
    }
    return GiftManager(liveID: liveID, language: languageCode)
}
```

## 调用时序

```
进房成功
    │
    ▼
GiftStore.create(liveID:)              // 创建实例
    │
    ├─ setLanguage("zh-CN")            // （可选）多语言设置
    │
    ▼
订阅 giftEventPublisher                // ⚠️ 进房后立即订阅，避免遗漏礼物
    │
    ├─ 用户打开礼物面板
    │       │
    │       ▼
    │   refreshUsableGifts()           // 拉取礼物分类+列表
    │       │
    │       ├─ .failure → 展示错误，提供重试
    │       └─ .success → GiftState.usableGifts 更新 → 渲染面板
    │
    ├─ 用户点击发送礼物
    │       │
    │       ▼
    │   sendGift(giftID:count:)
    │       ├─ .failure(-4001) → 引导充值
    │       ├─ .failure(-4002) → 刷新礼物列表
    │       └─ .success → （无需额外操作）
    │
    ├─ 收到 giftEventPublisher 事件
    │       │
    │       ▼
    │   .onReceiveGift(giftInfo)
    │       ├─ 播放礼物动画（resourceURL）
    │       └─ 弹幕区插入礼物提示
    │
    └─ 退出直播间
            │
            ▼
        cancellables.removeAll()
```

## 平台特有注意事项

### 1. 礼物动画资源预加载
`Gift.resourceURL` 指向动画文件（如 SVGA、MP4）。建议在 `refreshUsableGifts` 成功后异步预下载高频礼物动画文件到本地缓存，避免发送时实时下载导致动画延迟。

### 2. 连击礼物（连续发送相同礼物）
iOS 上实现连击需在 UI 层维护连击计数和防抖 Timer（建议 800ms 间隔）。收到 `onReceiveGift` 后判断是否与上一条礼物来自同一发送者且礼物相同，若是则累计数量更新 UI，否则重新播放动画。

### 3. 内存管理
礼物动画（SVGA/Lottie）占用内存较高。建议同时最多播放 3 个礼物动画，超出时将旧动画排队等待完成后再播放，使用动画队列管理器控制并发数。

### 4. 礼物面板手势冲突
礼物面板通常以半屏弹出。注意与直播间的手势识别冲突（如 scrollView 的滑动手势），可通过 `UIGestureRecognizerDelegate` 的 `shouldRecognizeSimultaneously` 处理。
