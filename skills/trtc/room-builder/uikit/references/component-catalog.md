# TRTC Room UIKit · 组件目录

> 本文件是组件的完整目录，包含每个组件的 class 名、HTML 范式、变体和状态类。
> 生成 room 类产品界面时，**必须严格使用以下组件和 class 名**，禁止自行发明。

---

## 一、Atoms（原子组件 · 25 个）

### 1. ui-btn · 按钮
```html
<button class="ui-btn ui-btn--{variant}">文字</button>
```
**变体**：`--primary`（蓝底白字）| `--ghost`（白底蓝边）| `--danger`（白底红边）| `--text`（纯文字）| `--end`（结束房间 pill）| `--copy`（小蓝实心）| `--invite`（邀请 pill）| `--send`（聊天发送）| `--scope`（超轻次级）
**尺寸**：`--xs` | `--sm` | `--md`（默认）| `--lg`
**状态**：`.is-disabled` / `[disabled]`

### 2. ui-avatar · 头像
```html
<span class="ui-avatar ui-avatar--{size}" style="background-image:url('{img}')"></span>
```
**尺寸**：`--sm`（28px）| `--md`（36px）| `--lg`（48px）

### 3. ui-badge · 徽章
```html
<span class="ui-badge ui-badge--dark">内容</span>
```
**变体**：`--dark`（深色浮于视频上）
**状态**：`.is-hidden` / `.is-show`

### 4. ui-dot · 状态圆点
```html
<span class="ui-dot ui-dot--{variant}"></span>
```
**变体**：`--success`（绿）| `--danger`（红）| `--ring`（带外圈）
**组合**：`ui-dot--ring ui-dot--danger`（录制中红点）

### 5. ui-caret · 箭头
```html
<span class="ui-caret ui-caret--down"></span>
```
**方向**：`--down` | `--up` | `--right`
**尺寸**：`--sm`（小号）
**状态**：`.is-interactive`（可点击悬浮变色）

### 6. ui-divider · 分割线
```html
<hr class="ui-divider ui-divider--h" />
```
**方向**：`--h`（水平）| `--v`（垂直）

### 7. ui-icon · 图标容器
```html
<svg class="ui-icon ui-icon--{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
  <!-- SVG path -->
</svg>
```
**尺寸**：`--xs`（14px）| `--sm`（16px）| `--md`（18px）| `--lg`（22px）| `--xl`（26px）
**颜色修饰**：`--inherit`（继承父色）| `--success`（绿色）| `--danger`（红色）| `--icon-muted`（弱灰）

### 8. ui-icon-slash · 斜杠覆盖层
```html
<span class="ui-icon-slot">
  <svg class="ui-icon ui-icon--lg ui-icon--inherit">...</svg>
  <span class="ui-icon-slash" aria-hidden="true"></span>
</span>
```
**用途**：麦克风关闭 / 摄像头关闭时叠加在图标上的红色斜杠

### 9. ui-input · 输入框
```html
<input class="ui-input" placeholder="搜索成员" />
```

### 10. ui-select · 下拉选择
```html
<select class="ui-select"><option>选项</option></select>
```

### 11. ui-label · 表单标签
```html
<label class="ui-label ui-label--fixed-100">设备</label>
```
**变体**：`--fixed-100`（固定 100px 宽度）

### 12. ui-level-bar · 音量条
```html
<div class="ui-level-bar"><div class="ui-level-bar__fill" style="--level: 42%"></div></div>
```
**数据驱动**：`--level` CSS 变量控制填充百分比

### 13. ui-tag · 标签/标题
```html
<div class="ui-tag ui-tag--{variant}">文字</div>
```
**变体**：`--section-title`（菜单区域标题）| `--h4`（表单小标题）

### 14. ui-link · 链接
```html
<a class="ui-link">复制</a>
```
**状态**：`.ui-link--success`（操作成功后变绿）

### 15. ui-spacer · 弹性占位
```html
<div class="ui-spacer"></div>
```

### 16. ui-sr-only · 无障碍隐藏
```html
<span class="ui-sr-only">仅屏幕阅读器可见</span>
```

### 17. ui-check · 勾选图标
```html
<svg class="ui-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l5 5L20 7"/></svg>
```
**状态**：`.is-hidden`（未选中时隐藏但占位）

### 18. ui-level-seg · 分段音量条
```html
<div class="ui-level-seg">
  <span class="ui-level-seg__bar is-on"></span>
  <span class="ui-level-seg__bar is-on"></span>
  <span class="ui-level-seg__bar is-on"></span>
  <span class="ui-level-seg__bar"></span>
  <span class="ui-level-seg__bar"></span>
</div>
```
**说明**：每格 3x6px，间距 3px，`.is-on` 为亮色（品牌色）

### 19. ui-num-badge · 数字角标
```html
<span class="ui-num-badge">
  <img class="ui-icon ui-icon--md" src="assets/icons/icon-chat.svg" />
  <span class="ui-num-badge__count">2</span>
</span>
```
**状态**：`.is-hidden`（隐藏角标数字）

### 20. ui-select-box · 自定义下拉选择框
```html
<div class="ui-select-box">
  <span class="ui-select-box__text">默认-外置麦克风</span>
  <img class="ui-select-box__arrow" src="assets/settings/arrow-down.svg" />
</div>
```
**变体**：`--muted`（文字浅灰色）

### 21. ui-share-card · 屏幕分享缩略卡片
```html
<div class="ui-share-card">
  <img class="ui-share-card__thumb" src="assets/share/screen-thumb-1.png" />
  <span class="ui-share-card__name">桌面一</span>
</div>
```
**状态**：`.is-selected`（蓝色边框）| `.is-active`（蓝色填充 + 白字，正在分享中）

### 22. ui-toast · 全局提示
```html
<div class="ui-toast ui-toast--dark is-show">当前您的网络状态不佳</div>
<div class="ui-toast ui-toast--success is-show">
  <img class="ui-icon ui-icon--sm" src="assets/icons/icon-check-green.svg" /> 复制成功
</div>
<div class="ui-toast ui-toast--error is-show">
  <img class="ui-icon ui-icon--sm" src="assets/icons/icon-error-circle.svg" /> 密码错误
</div>
```
**变体**：`--dark`（深色半透明）| `--success`（浅绿底）| `--error`（浅红底）
**状态**：`.is-show`（显示，默认隐藏）

### 23. ui-toggle · 开关切换
```html
<label class="ui-toggle is-on">
  <input type="checkbox" checked />
  <span class="ui-toggle__track"></span>
  <span class="ui-toggle__thumb"></span>
</label>
```
**状态**：`.is-on`（蓝底 + thumb 右移）

### 24. ui-spinner · 加载动画
```html
<div class="ui-spinner">
  <div class="ui-spinner__ring"></div>
  <span class="ui-spinner__text">正在进入房间...</span>
</div>
```
**变体**：`--sm`（24px 小号无文字）| `--lg`（48px 大号）
**动画**：自带 CSS @keyframes 旋转

### 25. ui-password-input · 密码输入框
```html
<div class="ui-password-input">
  <input class="ui-password-input__field" type="password" placeholder="请输入入会密码" />
  <button class="ui-password-input__toggle" data-action="toggle-pw">
    <img class="ui-icon ui-icon--sm" src="assets/icons/icon-eye-off.svg" />
  </button>
</div>
```
**状态**：`.is-visible`（密码可见态，切换图标为 eye-on）

---

## 二、Molecules（分子组件 · 24 个）

### 1. ui-icon-button · 图标按钮（底栏核心）
```html
<div class="ui-icon-button" data-btn="share">
  <span class="ui-icon-button__icon">
    <svg class="ui-icon ui-icon--lg ui-icon--inherit">...</svg>
  </span>
  <span class="ui-icon-button__label">共享屏幕</span>
</div>
```
**状态**：`.is-active`（选中蓝色）| `.is-off`（关闭红色+斜杠）| `.is-warning`（举手橙色）

### 2. ui-icon-button--with-caret · 带下拉箭头的图标按钮
```html
<div class="ui-icon-button ui-icon-button--with-caret" data-btn="mic">
  <span class="ui-icon-button__iconrow">
    <span class="ui-icon-button__icon" data-action="toggle-mic">
      <span class="ui-icon-slot">
        <svg class="ui-icon ui-icon--lg ui-icon--inherit">...</svg>
        <span class="ui-icon-slash" aria-hidden="true"></span>
      </span>
    </span>
    <span class="ui-caret ui-caret--down ui-caret--sm is-interactive" data-pop="mic"></span>
  </span>
  <span class="ui-icon-button__label">麦克风</span>
</div>
```

### 3. ui-toolbar-item · 顶栏工具项
```html
<div class="ui-toolbar-item" data-tb="layout">
  <svg class="ui-icon ui-icon--md">...</svg>
  <span>布局</span>
</div>
```
**状态**：`.is-active`（弹出 popover 时）| `.is-stable`（网络稳定绿色）

### 4. ui-search-input · 搜索输入框
```html
<div class="ui-search-input">
  <svg class="ui-icon ui-icon--xs ui-search-input__icon">...</svg>
  <input class="ui-input" placeholder="搜索成员" />
</div>
```

### 5. ui-menu-item · 菜单项
```html
<div class="ui-menu-item">
  <svg class="ui-check">...</svg>
  <span>MacBook Pro 麦克风</span>
</div>
```

### 6. ui-menu-section · 菜单分区
```html
<div class="ui-menu-section">
  <div class="ui-tag ui-tag--section-title">选择麦克风</div>
  <div class="ui-menu-item">...</div>
</div>
```

### 7. ui-list-row · 成员列表行
```html
<div class="ui-list-row">
  <span class="ui-avatar ui-avatar--md" style="background-image:url('{img}')"></span>
  <span class="ui-list-row__name">用户名</span>
  <span class="ui-list-row-actions">
    <!-- 状态图标 -->
  </span>
</div>
```

### 8. ui-list-row-actions · 列表行操作区
```html
<span class="ui-list-row-actions">
  <span class="ui-dot ui-dot--ring ui-dot--danger"></span>
  <svg class="ui-icon ui-icon--sm">...</svg>
</span>
```

### 9. ui-chat-message · 聊天消息
```html
<!-- 他人消息 -->
<div class="ui-chat-message">
  <div class="ui-chat-message__meta"><b>用户名</b>10:23</div>
  <div class="ui-chat-message__bubble">消息内容</div>
</div>
<!-- 自己消息 -->
<div class="ui-chat-message ui-chat-message--me">
  <div class="ui-chat-message__meta">10:24<b>我</b></div>
  <div class="ui-chat-message__bubble">消息内容</div>
</div>
```

### 10. ui-chat-toolbar · 聊天工具栏
```html
<div class="ui-chat-toolbar">
  <svg class="ui-icon ui-icon--md"><!-- 表情 --></svg>
  <svg class="ui-icon ui-icon--md"><!-- 图片 --></svg>
  <svg class="ui-icon ui-icon--md"><!-- 文件 --></svg>
</div>
```

### 11. ui-form-row · 表单行
```html
<div class="ui-form-row">
  <label class="ui-label ui-label--fixed-100">设备</label>
  <select class="ui-select">...</select>
</div>
```

### 12. ui-info-row · 信息行（键值对）
```html
<div class="ui-info-row ui-info-row--key-fixed-90">
  <span class="ui-info-row__key">房间号</span>
  <span class="ui-info-row__value">938 234 230</span>
  <span class="ui-info-row__action"><a class="ui-link">复制</a></span>
</div>
```
**变体**：`--key-fixed-90`（键宽固定 90px）| `--dashed`（虚线下边框）

### 13. ui-nav-item · 导航项（设置 modal 侧栏）
```html
<div class="ui-nav-item is-active" data-nav="audio">音频</div>
```
**状态**：`.is-active`

### 14. ui-layout-preview-card · 布局预览卡片
```html
<div class="ui-layout-preview-card is-selected" data-layout="nine">
  <div class="ui-layout-thumb ui-layout-thumb--nine">...</div>
  <div class="ui-layout-preview-card__name">一屏九等分</div>
</div>
```
**状态**：`.is-selected`

### 15. ui-layout-thumb · 布局缩略图
```html
<div class="ui-layout-thumb ui-layout-thumb--{variant}">
  <div class="ui-layout-thumb__cell"></div>
  <!-- ... -->
</div>
```
**变体**：`--nine`（九宫格）| `--right-list`（右侧列表）| `--top-list`（顶部列表）
**特殊 cell**：`ui-layout-thumb__cell--main`（主屏大格）

### 16. ui-signal-row · 网络信号行
```html
<div class="ui-signal-row">
  <span class="ui-signal-row__key">延迟</span>
  <span class="ui-signal-row__value">53 ms</span>
</div>
```
**变体**：`--loss`（丢包率行，含上下箭头）

### 17. ui-user-pill · 用户胶囊
```html
<div class="ui-user-pill">
  <span class="ui-avatar ui-avatar--sm" style="background-image:url('{img}')"></span>
  <span class="ui-user-pill__name">用户ID</span>
  <span class="ui-caret ui-caret--down ui-caret--sm"></span>
</div>
```

### 18. ui-lang-select · 语言选择
```html
<div class="ui-lang-select">
  <svg class="ui-icon ui-icon--md ui-icon--success">...</svg>
  <span>中文</span>
</div>
```

### 19. ui-video-badge · 视频瓦片角标
```html
<!-- 标准（头像 + 名字 + 麦克风） -->
<div class="ui-video-badge">
  <span class="ui-video-badge__avatar">
    <img class="ui-icon" src="蓝圆底.svg" />
    <img class="ui-icon ui-video-badge__avatar-icon" src="人形.svg" />
  </span>
  <span class="ui-video-badge__name">李子明</span>
  <span class="ui-video-badge__mic"><img class="ui-icon" src="麦克风.svg" /></span>
</div>
<!-- 紧凑（无头像） -->
<div class="ui-video-badge ui-video-badge--compact">
  <span class="ui-video-badge__mic"><img class="ui-icon" src="麦克风.svg" /></span>
  <span class="ui-video-badge__name">张凯文</span>
</div>
```
**变体**：`--compact`（紧凑无头像）
**位置**：绝对定位在视频瓦片左下角

### 20. ui-tree-item · 通讯录树节点
```html
<!-- 部门节点 -->
<div class="ui-tree-item ui-tree-item--l0">
  <img class="ui-tree-item__check" src="assets/contact/checkbox-off.svg" />
  <img class="ui-tree-item__arrow" src="assets/contact/arrow-right.svg" />
  <span class="ui-tree-item__label">产品部</span>
</div>
<!-- 人员节点 -->
<div class="ui-tree-item ui-tree-item--l3">
  <img class="ui-tree-item__check" src="assets/contact/checkbox-off.svg" />
  <img class="ui-tree-item__avatar" src="assets/contact/avatar-1.svg" />
  <span class="ui-tree-item__label ui-tree-item__label--person">张三</span>
</div>
```
**层级**：`--l0`（根）| `--l1`（部门）| `--l2`（小组）| `--l3`（人员）
**状态**：`.is-open`（箭头旋转 90°，展开子节点）

### 21. ui-camera-preview · 摄像头预览卡
```html
<div class="ui-camera-preview">
  <img class="ui-camera-preview__video" src="..." />
</div>
<!-- 关闭态 -->
<div class="ui-camera-preview is-off">
  <div class="ui-camera-preview__placeholder">
    <img class="ui-icon ui-icon--xl" src="assets/icons/icon-user.svg" />
    <span class="ui-camera-preview__hint">暂无摄像画面</span>
  </div>
</div>
```
**状态**：`.is-off`（摄像头关闭，显示头像占位）
**尺寸**：默认 420×320px，可通过 `--layout-lobby-preview-w/h` token 调整

### 22. ui-room-card · 历史房间卡片
```html
<div class="ui-room-card">
  <div class="ui-room-card__info">
    <span class="ui-room-card__name">jason的临时房间</span>
    <span class="ui-room-card__meta">11:30 - 14:30 | 567 428 829</span>
  </div>
  <span class="ui-room-card__status ui-room-card__status--active">进行中</span>
  <div class="ui-room-card__actions">
    <button class="ui-btn ui-btn--copy">加入</button>
  </div>
</div>
```
**状态标签**：`--active`（蓝色/进行中）| `--pending`（红色/未开始）| `--ended`（灰色/已结束）
**交互**：hover 时显示 `__actions` 操作按钮

### 23. ui-device-strip · 设备预检栏
```html
<div class="ui-device-strip">
  <div class="ui-device-strip__item">
    <img class="ui-icon ui-icon--md" src="assets/icons/icon-mic.svg" />
    <span class="ui-caret ui-caret--down ui-caret--sm"></span>
    <span class="ui-device-strip__label">麦克风</span>
  </div>
  <div class="ui-device-strip__item">
    <img class="ui-icon ui-icon--md" src="assets/icons/icon-cam.svg" />
    <span class="ui-caret ui-caret--down ui-caret--sm"></span>
    <span class="ui-device-strip__label">视频</span>
  </div>
</div>
```
**状态**：`__item.is-off`（设备关闭，红色图标）

### 24. ui-action-bar · 操作按钮组
```html
<div class="ui-action-bar">
  <button class="ui-action-bar__btn ui-action-bar__btn--primary">
    <img class="ui-icon ui-icon--sm" src="..." /> 新建房间
  </button>
  <button class="ui-action-bar__btn ui-action-bar__btn--secondary">
    <img class="ui-icon ui-icon--sm" src="..." /> 预定房间
  </button>
</div>
```
**变体**：`--primary`（实心主色）| `--secondary`（描边）

---

## 三、Organisms（组织组件 · 11 个）

### 1. ui-topbar · 顶栏
```html
<header class="ui-topbar">
  <div class="ui-topbar__left"><!-- toolbar-items --></div>
  <div class="ui-topbar__center">
    <span class="ui-topbar__title">会议名称<span class="ui-caret ui-caret--down"></span></span>
    <span class="ui-topbar__time">00:24</span>
  </div>
  <div class="ui-topbar__right"><!-- user-pill, lang-select --></div>
</header>
```

### 2. ui-bottombar · 底栏
```html
<footer class="ui-bottombar">
  <div class="ui-bottombar__left"><!-- mic, cam --></div>
  <div class="ui-bottombar__center"><!-- 功能按钮 --></div>
  <div class="ui-bottombar__right"><button class="ui-btn ui-btn--end">结束房间</button></div>
</footer>
```

### 3. ui-stage · 视频舞台
```html
<section class="ui-stage">
  <div class="ui-stage__frame" data-off-text="摄像头已关闭"
       style="--stage-off-avatar: url('{img}');">
    <span class="ui-badge ui-badge--dark is-hidden">我已静音</span>
    <img class="ui-stage__video" src="{video_or_image}" />
  </div>
</section>
```
**状态**：`.is-off`（摄像头关闭，显示头像 + 文字）

### 4. ui-side-panel · 侧栏
```html
<aside class="ui-side-panel is-open" data-active="members">
  <div class="ui-side-panel__content" data-panel="members">...</div>
  <div class="ui-side-panel__content" data-panel="chat">...</div>
</aside>
```
**状态**：`.is-open`
**`data-active`**：控制显示哪个面板

### 5. ui-side-panel__header · 侧栏头部
```html
<div class="ui-side-panel__header">
  <div class="ui-side-panel__title">成员 (4)</div>
  <div class="ui-side-panel__close"><!-- close icon --></div>
</div>
```

### 6. ui-popover · 弹出层
```html
<div class="ui-popover ui-popover--{position}" id="pop-xxx">
  <!-- 内容 -->
</div>
```
**位置**：`--top`（顶栏向下）| `--bottom`（底栏向上）| `--top-center`（居中向下）
**宽度**：`--min-180` | `--min-240` | `--min-440` | `--min-460`
**状态**：`.is-open`（显示）

### 7. ui-modal · 模态弹窗
```html
<div class="ui-modal" id="modal-settings">
  <div class="ui-modal__box">
    <div class="ui-modal__header">...</div>
    <div class="ui-modal__body">...</div>
  </div>
</div>
```
**变体**：`.ui-modal--invite`（邀请弹窗窄版）
**状态**：`.is-open`

### 8. ui-modal__header · 弹窗头部
```html
<div class="ui-modal__header">
  <div class="ui-modal__title">设置</div>
  <div class="ui-modal__close">×</div>
</div>
```

### 9. ui-modal__body · 弹窗主体
```html
<div class="ui-modal__body">
  <div class="ui-modal__sidebar"><!-- nav-items --></div>
  <div class="ui-modal__main"><!-- 内容 --></div>
</div>
```
**变体**：`--flat`（无侧栏模式）
**子变体**：`ui-modal__main--full`（占满宽度）| `ui-modal__main--wide`（更宽间距）

### 10. ui-chat-input · 聊天输入区
```html
<div class="ui-chat-input">
  <div class="ui-chat-toolbar"><!-- 工具图标 --></div>
  <textarea class="ui-textarea ui-chat-input__textarea" placeholder="发送给所有人"></textarea>
  <div class="ui-chat-input__send">
    <button class="ui-btn ui-btn--send">发送</button>
  </div>
</div>
```

### 11. ui-room-list · 历史房间列表
```html
<div class="ui-room-list">
  <div class="ui-room-list__header">
    <a class="ui-room-list__link">历史房间 →</a>
  </div>
  <div class="ui-room-list__body">
    <div class="ui-room-list__date">
      <img class="ui-icon ui-icon--xs" src="..." /> 2022年12月06日
    </div>
    <div class="ui-room-card">...</div>
    <div class="ui-room-card">...</div>
  </div>
</div>
```
**尺寸**：宽 320px，max-height 420px（超出滚动）
**用途**：会前大厅页右侧的历史房间列表

---

## 四、页面骨架

### mc-app · 根容器
```html
<div class="mc-app" id="app">
  <header class="ui-topbar">...</header>
  <section class="ui-stage">...</section>
  <aside class="ui-side-panel">...</aside>
  <footer class="ui-bottombar">...</footer>
</div>
```
**状态**：`.is-panel-open`（侧栏打开，三栏让位）
**`data-panel`**：当前打开的面板名

### 布局机制
- 三行 Grid：`topbar | stage | bottombar`
- 侧栏绝对定位于右侧
- 侧栏打开时，topbar/stage/bottombar 宽度变为 `calc(100vw - var(--layout-side-w))`

---

## 五、通用状态类速查

| 类 | 用途 |
|---|---|
| `.is-active` | 激活/选中 |
| `.is-open` | 展开/显示 |
| `.is-selected` | 持久选中 |
| `.is-off` | 关闭功能（红+斜杠） |
| `.is-on` | 开启 |
| `.is-disabled` | 不可交互 |
| `.is-loading` | 加载中 |
| `.is-hidden` / `.is-show` | 显隐 |
| `.is-muted` | 静音/弱化 |
| `.is-interactive` | 可点击 |
| `.is-truncate` | 单行省略 |
| `.is-warning` | 警告（橙色） |
| `.is-stable` | 网络稳定（绿色） |

---

## 六、CSS 引入方式

### 全量引入
```html
<html data-theme="mc">
<head>
  <link rel="stylesheet" href="themes/meeting-classic/index.css">
</head>
```

### 按需引入（最小集）
```html
<link rel="stylesheet" href="themes/meeting-classic/tokens.css">  <!-- 必须 -->
<link rel="stylesheet" href="themes/meeting-classic/layout.css">  <!-- 页面骨架 -->
<link rel="stylesheet" href="themes/meeting-classic/components/atoms/button.css">  <!-- 按需 -->
```

### 引入顺序
1. `tokens.css` → 2. `layout.css` → 3. atoms → 4. molecules → 5. organisms

### 暗色模式
```html
<html data-theme="mc" data-mode="dark">
<head>
  <link rel="stylesheet" href="themes/meeting-classic/index.css">
  <link rel="stylesheet" href="themes/meeting-classic/tokens.dark.css">
</head>
```
- `tokens.dark.css` 必须在 `tokens.css`（或 `index.css`）之后加载
- 通过 `data-mode="dark"` 激活，只覆盖 L1 令牌，L2 自动跟随
- 运行时切换：`document.documentElement.dataset.mode = 'dark'`

### SVG 图标资产
新版组件库内置了完整的 SVG 图标集，位于 `assets/` 目录下：
- `assets/icons/` — 通用图标（麦克风、摄像头、共享等）
- `assets/contact/` — 通讯录图标（头像、复选框、箭头等）
- `assets/members/` — 成员管理图标（角色徽章、操作按钮等）
- `assets/settings/` — 设置面板图标（箭头、开关等）
- `assets/share/` — 屏幕分享图标和缩略图
- `assets/stage/` — 视频舞台图标和占位图
