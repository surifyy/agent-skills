---
id: live/coguest-apply
platform: ios
---

# 观众申请连麦 — iOS 实现

## 前置条件

**依赖安装（Podfile）**
```ruby
pod 'AtomicXCore', '~> 4.0'
```

**Info.plist 权限声明**（连麦需要摄像头与麦克风权限）
```xml
<key>NSCameraUsageDescription</key>
<string>连麦时需要访问摄像头</string>
<key>NSMicrophoneUsageDescription</key>
<string>连麦时需要访问麦克风</string>
```

**前置状态**：
- `LoginStore.shared.isLogin == true`（登录成功）
- 已进入直播间，持有有效的 `liveID`
- `CoGuestStore` 已通过 `create(liveID:)` 初始化

## API 调用

```swift
// ── 初始化 ─────────────────────────────────────────────────────
let coGuestStore = CoGuestStore.create(liveID: String)

// ── 观众端 ─────────────────────────────────────────────────────
// 发起连麦申请；seatIndex 默认 -1（自动分配），timeout 单位为秒，推荐 30
coGuestStore.applyForSeat(
    seatIndex: Int,            // 默认 -1，自动分配麦位
    timeout: TimeInterval,
    extraInfo: String?,
    completion: CompletionClosure?
)
// CompletionClosure = (Result<Void, ErrorInfo>) -> Void

// 撤回申请（主播响应前可用）
coGuestStore.cancelApplication(completion: CompletionClosure?)

// 接受主播邀请
// ⚠️ 参数为 inviterID（邀请方），不是 userID
coGuestStore.acceptInvitation(inviterID: String, completion: CompletionClosure?)

// 拒绝主播邀请
coGuestStore.rejectInvitation(inviterID: String, completion: CompletionClosure?)

// ── 主播端 ─────────────────────────────────────────────────────
// 同意连麦申请
coGuestStore.acceptApplication(userID: String, completion: CompletionClosure?)

// 拒绝连麦申请
coGuestStore.rejectApplication(userID: String, completion: CompletionClosure?)

// 邀请观众上麦
coGuestStore.inviteToSeat(
    userID: String,
    seatIndex: Int,
    timeout: TimeInterval,
    extraInfo: String?,
    completion: CompletionClosure?
)

// 取消邀请
coGuestStore.cancelInvitation(inviteeID: String, completion: CompletionClosure?)

// ── 断开连麦（主播/观众均可调用）──────────────────────────────
coGuestStore.disConnect(completion: CompletionClosure?)

// ── 事件订阅 ───────────────────────────────────────────────────
coGuestStore.hostEventPublisher   // PassthroughSubject<HostEvent, Never>
coGuestStore.guestEventPublisher  // PassthroughSubject<GuestEvent, Never>
```

### HostEvent 枚举（完整，主播端）

| 事件 | 说明 |
|------|------|
| `.onGuestApplicationReceived(guestUser: LiveUserInfo)` | 收到观众连麦申请 |
| `.onGuestApplicationCancelled(guestUser: LiveUserInfo)` | 观众撤回了申请 |
| `.onGuestApplicationProcessedByOtherHost(guestUser: LiveUserInfo, hostUser: LiveUserInfo)` | 申请已被其他主播处理 |
| `.onHostInvitationResponded(isAccept: Bool, guestUser: LiveUserInfo)` | 被邀请观众已响应（同意/拒绝） |
| `.onHostInvitationNoResponse(guestUser: LiveUserInfo, reason: NoResponseReason)` | 被邀请观众未响应（超时） |

### GuestEvent 枚举（完整，观众端）

| 事件 | 说明 |
|------|------|
| `.onHostInvitationReceived(hostUser: LiveUserInfo)` | 收到主播邀请 |
| `.onHostInvitationCancelled(hostUser: LiveUserInfo)` | 主播取消了邀请 |
| `.onGuestApplicationResponded(isAccept: Bool, hostUser: LiveUserInfo)` | 申请被响应（isAccept: true 通过，false 拒绝） |
| `.onGuestApplicationNoResponse(reason: NoResponseReason)` | 申请超时无响应 |
| `.onKickedOffSeat(seatIndex: Int, hostUser: LiveUserInfo)` | 被主播踢下麦位 |

## 代码示例

### 观众端：申请 → 等待 → 开设备 → 连麦 → 断开

```swift
import AtomicXCore
import Combine

final class AudienceCoGuestViewModel: ObservableObject {

    // MARK: 状态

    enum CoGuestStatus {
        case idle           // 未连麦
        case applying       // 申请中
        case connected      // 连麦中
    }

    @Published var status: CoGuestStatus = .idle
    @Published var errorMessage: String?

    private let coGuestStore: CoGuestStore
    private var cancellables = Set<AnyCancellable>()
    private let applyTimeout: TimeInterval = 30

    init(liveID: String) {
        self.coGuestStore = CoGuestStore.create(liveID: liveID)
        observeGuestEvents()
    }

    // MARK: - 观众端事件订阅

    private func observeGuestEvents() {
        coGuestStore.guestEventPublisher
            .receive(on: DispatchQueue.main)
            .sink { [weak self] event in
                guard let self else { return }
                switch event {
                case .onGuestApplicationResponded(let isAccept, let hostUser):
                    if isAccept {
                        // ✅ 申请通过，立即开启设备
                        print("[CoGuest] 主播 \(hostUser.userName) 已同意申请")
                        self.openDevicesAfterAccepted()
                    } else {
                        // 申请被拒绝
                        self.status = .idle
                        self.errorMessage = "连麦申请被主播拒绝"
                    }

                case .onGuestApplicationNoResponse(let reason):
                    // 超时未响应
                    self.status = .idle
                    self.errorMessage = "申请超时，请重试"
                    print("[CoGuest] 申请超时，原因: \(reason)")

                case .onKickedOffSeat(let seatIndex, let hostUser):
                    // 被主播踢下麦位
                    self.closeDevicesAfterDisconnect()
                    self.status = .idle
                    self.errorMessage = "已被主播移出麦位（座位 \(seatIndex)）"
                    print("[CoGuest] 被 \(hostUser.userName) 踢下麦位 \(seatIndex)")

                case .onHostInvitationReceived(let hostUser):
                    // 收到主播邀请，可展示弹窗供用户选择
                    print("[CoGuest] 收到主播 \(hostUser.userName) 的邀请")

                case .onHostInvitationCancelled(let hostUser):
                    // 主播取消邀请
                    print("[CoGuest] 主播 \(hostUser.userName) 取消了邀请")
                }
            }
            .store(in: &cancellables)
    }

    // MARK: - 申请连麦
    // seatIndex: Int 默认 -1 表示自动分配麦位

    func applyForSeat(seatIndex: Int = -1) {
        guard status == .idle else { return }
        status = .applying

        coGuestStore.applyForSeat(
            seatIndex: seatIndex,
            timeout: applyTimeout,
            extraInfo: nil
        ) { [weak self] result in
            guard let self else { return }
            DispatchQueue.main.async {
                switch result {
                case .success:
                    // 申请发送成功，等待主播响应（通过 guestEventPublisher 回调）
                    print("[CoGuest] 申请已发送，等待主播响应...")
                case .failure(let error):
                    self.status = .idle
                    if error.code == -2340 {
                        self.errorMessage = "当前连麦人数已达上限，请稍后再试"
                    } else {
                        self.errorMessage = "申请失败：\(error.message)"
                    }
                }
            }
        }
    }

    // MARK: - 取消申请

    func cancelApplication() {
        guard status == .applying else { return }
        coGuestStore.cancelApplication { [weak self] _ in
            DispatchQueue.main.async {
                self?.status = .idle
            }
        }
    }

    // MARK: - 接受主播邀请（inviterID 为邀请方主播的 userID）

    func acceptInvitation(inviterID: String) {
        coGuestStore.acceptInvitation(inviterID: inviterID) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success:
                    self?.openDevicesAfterAccepted()
                case .failure(let error):
                    self?.errorMessage = "接受邀请失败：\(error.message)"
                }
            }
        }
    }

    // MARK: - 拒绝主播邀请

    func rejectInvitation(inviterID: String) {
        coGuestStore.rejectInvitation(inviterID: inviterID) { result in
            if case .failure(let error) = result {
                print("[CoGuest] 拒绝邀请失败 code=\(error.code)")
            }
        }
    }

    // MARK: - 申请通过后开设备

    private func openDevicesAfterAccepted() {
        // 先开麦克风
        DeviceStore.shared.openLocalMicrophone { [weak self] micResult in
            guard let self else { return }
            switch micResult {
            case .failure(let error):
                print("[CoGuest] 麦克风打开失败 code=\(error.code)")
                self.errorMessage = "麦克风打开失败，请检查权限"
                // 麦克风失败，断开连麦
                self.coGuestStore.disConnect(completion: nil)
                DispatchQueue.main.async { self.status = .idle }
            case .success:
                // 再开摄像头
                DeviceStore.shared.openLocalCamera(isFront: true) { cameraResult in
                    DispatchQueue.main.async {
                        if case .failure(let error) = cameraResult {
                            print("[CoGuest] 摄像头打开失败 code=\(error.code)，以纯音频模式连麦")
                        }
                        self.status = .connected
                    }
                }
            }
        }
    }

    // MARK: - 主动断开连麦

    func disconnect() {
        guard status == .connected else { return }
        coGuestStore.disConnect { [weak self] _ in
            self?.closeDevicesAfterDisconnect()
            DispatchQueue.main.async { self?.status = .idle }
        }
    }

    // MARK: - 断开后关闭设备

    private func closeDevicesAfterDisconnect() {
        DeviceStore.shared.closeLocalCamera()
        DeviceStore.shared.closeLocalMicrophone()
        print("[CoGuest] 连麦已断开，设备已关闭")
    }
}
```

---

### 主播端：监听申请 → 同意 / 拒绝 → 邀请 → 管理连麦

```swift
import AtomicXCore
import Combine

final class HostCoGuestViewModel: ObservableObject {

    // MARK: 状态

    @Published var pendingApplicants: [LiveUserInfo] = []   // 待审批申请列表
    @Published var connectedGuests: [SeatUserInfo]  = []    // 当前连麦列表

    private let coGuestStore: CoGuestStore
    private var cancellables = Set<AnyCancellable>()

    init(liveID: String) {
        self.coGuestStore = CoGuestStore.create(liveID: liveID)
        observeHostEvents()
        observeState()
    }

    // MARK: - 主播端事件订阅

    private func observeHostEvents() {
        coGuestStore.hostEventPublisher
            .receive(on: DispatchQueue.main)
            .sink { [weak self] event in
                guard let self else { return }
                switch event {
                case .onGuestApplicationReceived(let guestUser):
                    // 新收到观众申请，添加到待审批列表
                    if !self.pendingApplicants.contains(where: { $0.userID == guestUser.userID }) {
                        self.pendingApplicants.append(guestUser)
                    }

                case .onGuestApplicationCancelled(let guestUser):
                    // 观众撤回了申请
                    self.pendingApplicants.removeAll { $0.userID == guestUser.userID }

                case .onGuestApplicationProcessedByOtherHost(let guestUser, let hostUser):
                    // 申请被其他主播处理（多主播场景）
                    self.pendingApplicants.removeAll { $0.userID == guestUser.userID }
                    print("[Host] \(guestUser.userName) 的申请已被 \(hostUser.userName) 处理")

                case .onHostInvitationResponded(let isAccept, let guestUser):
                    if isAccept {
                        print("[Host] \(guestUser.userName) 接受了邀请")
                    } else {
                        print("[Host] \(guestUser.userName) 拒绝了邀请")
                    }

                case .onHostInvitationNoResponse(let guestUser, let reason):
                    print("[Host] \(guestUser.userName) 未响应邀请，原因: \(reason)")
                }
            }
            .store(in: &cancellables)
    }

    // MARK: - 状态订阅（实时同步连麦列表）

    private func observeState() {
        coGuestStore.state
            .map(\.connected)
            .receive(on: DispatchQueue.main)
            .assign(to: &$connectedGuests)
    }

    // MARK: - 同意申请

    func acceptApplication(userID: String) {
        coGuestStore.acceptApplication(userID: userID) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success:
                    self?.pendingApplicants.removeAll { $0.userID == userID }
                    print("[Host] 已同意 \(userID) 的连麦申请")
                case .failure(let error):
                    print("[Host] 同意申请失败 code=\(error.code) msg=\(error.message)")
                }
            }
        }
    }

    // MARK: - 拒绝申请

    func rejectApplication(userID: String) {
        coGuestStore.rejectApplication(userID: userID) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success:
                    self?.pendingApplicants.removeAll { $0.userID == userID }
                    print("[Host] 已拒绝 \(userID) 的连麦申请")
                case .failure(let error):
                    print("[Host] 拒绝申请失败 code=\(error.code) msg=\(error.message)")
                }
            }
        }
    }

    // MARK: - 主播邀请观众上麦

    func inviteToSeat(userID: String, seatIndex: Int = -1) {
        coGuestStore.inviteToSeat(
            userID: userID,
            seatIndex: seatIndex,
            timeout: 30,
            extraInfo: nil
        ) { result in
            if case .failure(let error) = result {
                print("[Host] 邀请失败 code=\(error.code) msg=\(error.message)")
            }
        }
    }

    // MARK: - 主播踢出已连麦观众

    func disconnectGuest() {
        coGuestStore.disConnect { result in
            DispatchQueue.main.async {
                if case .failure(let error) = result {
                    print("[Host] 断开失败 code=\(error.code) msg=\(error.message)")
                }
            }
        }
    }
}
```

## 调用时序

```
【观众端】
用户点击"申请连麦"
        │
        ▼
coGuestStore.applyForSeat(seatIndex: -1, timeout: 30, extraInfo: nil)
        │
        ├─ .failure(code: -2340) → 麦位满，提示用户
        ├─ .failure(ErrorInfo) → 展示 error.message
        │
        └─ .success（申请发出，等待主播响应）
                │
                ▼（guestEventPublisher 回调）
        .onGuestApplicationResponded(isAccept:hostUser:)
                │
                ├─ isAccept == false → 提示被拒，status = .idle
                │
                └─ isAccept == true
                        │
                        ▼
                openLocalMicrophone()
                        │
                        ├─ .failure → disConnect，提示权限问题
                        └─ .success
                                │
                                ▼
                        openLocalCamera(isFront: true)
                                └─ status = .connected（连麦中）

        .onKickedOffSeat(seatIndex:hostUser:) → closeDevices() → status = .idle
        .onGuestApplicationNoResponse(reason:) → status = .idle，提示超时

【主播端（并行）】
订阅 hostEventPublisher
        │
        ▼
.onGuestApplicationReceived(guestUser:) → 加入待审批列表
        │
        ├─ 主播点击"同意" → acceptApplication(userID:)
        │       └─ 从 pendingApplicants 移除
        └─ 主播点击"拒绝" → rejectApplication(userID:)
                └─ 从 pendingApplicants 移除

.onGuestApplicationCancelled(guestUser:) → 从待审批列表移除
```

## 平台特有注意事项

### 1. seatIndex 参数
`applyForSeat` 包含 `seatIndex: Int` 参数（默认值 `-1`），`-1` 表示由系统自动分配麦位。若业务有固定麦位布局（如卡拉 OK 多人），可传具体的麦位索引（从 0 开始）。

### 2. acceptInvitation / rejectInvitation 参数为 inviterID
观众接受/拒绝主播邀请时，参数名为 `inviterID`（邀请方），不是 `userID`。不要与 `acceptApplication(userID:)` 混淆，两者语义不同。

### 3. Combine cancellable 生命周期管理
`hostEventPublisher` 和 `guestEventPublisher` 是 Combine Publisher。订阅时返回的 `AnyCancellable` 必须存储到 ViewModel/ViewController 的属性中（如 `Set<AnyCancellable>`），否则订阅会立即被释放，导致主播收不到任何申请事件。

### 4. 连麦中 App 进入后台
iOS 系统进入后台时会挂起摄像头采集，但麦克风仍可持续（需在 `Info.plist` 开启 `audio` 后台模式）。连麦场景建议在 App 进入后台时关闭摄像头（`closeLocalCamera()`），避免观众看到定格画面。

### 5. `-2340` 麦位超限
错误码 `-2340` 由服务端返回，表示当前直播间连麦人数已达上限。此时应禁用"申请连麦"按钮，并订阅 `CoGuestState.connected` 列表变化：当连麦人数减少时，自动重新启用按钮。
