# TRTC Room UIKit（内部组件库）

> **位置**：`trtc/room-builder/uikit/`
> **定位**：本目录是 `trtc-room-builder` skill 的**内部组件库**，不是独立 skill。Standard 路径生成界面时所依赖的 60 个组件、Design Token、暗色模式、SVG 图标集和风格定制脚本均在此。
> **触发方式**：不对外暴露，仅由 `trtc/room-builder/SKILL.md` 的 Standard 路径调用。

TRTC Room UIKit 是一套面向 room 类音视频产品的生产级 UI 组件库。包含 60 个组件（原子/分子/组织三层），全部通过 Design Token 体系实现样式管理，支持品牌色、圆角、间距等风格的无损定制，并内置暗色模式和完整 SVG 图标集。

## 核心能力

1. **高还原度 UI 生成** — 使用预定义的 60 个组件和精确的 HTML 范式生成界面
2. **风格定制** — 通过覆盖 L1 token 实现品牌色、圆角等全局换肤
3. **暗色模式** — 内置 `tokens.dark.css`，通过 `data-mode="dark"` 一键切换
4. **框架无关** — 纯 HTML/CSS 实现，React/Vue/Svelte/原生 HTML 均可接入
5. **状态驱动** — 所有运行时状态通过 `.is-*` class 切换，零 inline style
6. **内置图标** — 完整 SVG 图标集，按场景分目录（icons/contact/members/settings/share/stage）

## 工作流程

### Phase 1：理解需求

收到 room 类产品搭建需求时：

1. 明确产品类型：视频会议 / 语音房间 / 直播间 / 连麦房
2. 明确需要的界面区域：顶栏、底栏、视频区、侧栏（成员/聊天）、弹窗（设置/邀请）
3. 明确风格需求：是否需要自定义品牌色、圆角偏好等

### Phase 2：读取组件参考

根据需求，读取以下参考文档：

- **组件目录**：`references/component-catalog.md`
  - 包含 60 个组件的完整 class 名、HTML 范式、变体和状态类
  - grep pattern: `### \d+\.` 可定位到每个组件
- **Token 契约**：`references/token-contract.md`
  - 包含全部 ~100 个 L2 令牌的清单和风格定制指南
  - grep pattern: `### ` 可定位到各 token 分类

### Phase 3：生成代码

#### 3.1 复制资产文件

将 `assets/themes/meeting-classic/` 目录复制到用户项目中：

```bash
cp -R {skill_dir}/assets/themes/meeting-classic {project}/themes/meeting-classic
```

#### 3.2 设置 HTML 骨架

```html
<!DOCTYPE html>
<html lang="zh-CN" data-theme="mc">
<head>
  <meta charset="UTF-8" />
  <!-- 全量引入 -->
  <link rel="stylesheet" href="themes/meeting-classic/index.css">
  <!-- 或按需引入 tokens.css + 需要的 components/*.css -->
</head>
<body>
  <div class="mc-app" id="app">
    <!-- 使用 component-catalog.md 中的 HTML 范式组装界面 -->
  </div>
</body>
</html>
```

#### 3.3 使用组件

**严格规则**：

1. **必须使用 `component-catalog.md` 中定义的 class 名和 HTML 结构**，禁止自行发明组件名
2. **所有样式通过 L2 token 引用**，禁止硬编码 `#xxx` / `rgba` / 固定 px
3. **运行时状态通过 `.is-*` class 切换**，禁止 inline style（数据驱动的 `background-image`、`--level`、`--stage-off-avatar` 除外）
4. **CSS 引入顺序**：tokens.css → (tokens.dark.css 如需暗色) → layout.css → atoms → molecules → organisms
5. **图标引用**：优先使用 `assets/` 目录下的内置 SVG 图标

#### 3.4 框架集成

- **React/Next.js**：全局引入 CSS，用 `className` 绑定组件 class，用 state 切换 `.is-*`
- **Vue 3**：全局引入 CSS，用 `:class` 绑定，用 `ref` 切换状态
- **原生 HTML**：直接用 class，用 `classList.toggle()` 切换状态

完整框架接入示例见 `assets/themes/meeting-classic/INTEGRATION.md`。

### Phase 4：风格定制（可选）

如果用户需要自定义风格：

#### 方式 A：自动生成覆盖文件

运行 `scripts/generate-theme-overrides.py`：

```bash
python3 {skill_dir}/scripts/generate-theme-overrides.py \
  --primary "#7c3aed" \
  --radius-scale 1.5 \
  --output {project}/themes/overrides.css
```

支持的参数：
- `--primary` — 品牌主色（hex），自动派生 hover/strong/bg/ring
- `--danger` — 危险色
- `--success` — 成功色
- `--warning` — 警告色
- `--radius-scale` — 圆角缩放倍数（1.0=默认，2.0=双倍圆润，0.5=更锐利）
- `--bg-base` — 主背景色
- `--text` — 主文字色
- `--font-family` — 自定义字体栈

然后在项目中引入：

```html
<link rel="stylesheet" href="themes/meeting-classic/tokens.css">
<link rel="stylesheet" href="themes/overrides.css">
<!-- 后续组件 CSS -->
```

#### 方式 B：手写覆盖

创建 `overrides.css`，只覆盖需要变更的 L1 令牌：

```css
[data-theme="mc"] {
  --mc-color-primary: #7c3aed;
  --mc-color-primary-hover: #6d28d9;
  --mc-radius-sm: 8px;
  --mc-radius-md: 12px;
}
```

覆盖规则：只修改 `--mc-*` 前缀的 L1 令牌，L2 别名自动跟随变化。
完整 token 清单查阅 `references/token-contract.md`。

#### 方式 C：图标品牌色替换

SVG 图标中的蓝色高亮（`#1C66E5`）可通过脚本批量替换为目标品牌色：

```bash
python3 {skill_dir}/scripts/recolor-icons.py --accent "#7c3aed"
```

支持的参数：
- `--accent` — 目标品牌色（替换蓝色高亮 #1C66E5）
- `--base` — 目标主体色（替换灰色 #4F586B，可选）
- `--secondary` — 目标次要色（替换浅灰 #6B758A，可选）
- `--dir` — 自定义 SVG 目录路径（默认为 skill 自身的 assets）
- `--dry-run` — 只预览不实际修改

**注意**：此脚本直接修改 SVG 文件。如需保留原版，先复制一份再操作。

## 组件清单速查

| 层级 | 数量 | 组件 |
|---|---|---|
| Atoms | 25 | btn, avatar, badge, dot, caret, divider, icon, icon-slash, input, select, select-box, label, level-bar, level-seg, tag, link, spacer, sr-only, check, share-card, toggle, toast, num-badge, spinner, password-input |
| Molecules | 24 | icon-button, icon-button-caret, toolbar-item, search-input, menu-item, menu-section, list-row, list-row-actions, chat-message, chat-toolbar, form-row, info-row, nav-item, layout-preview-card, layout-thumb, signal-row, user-pill, lang-select, video-badge, tree-item, camera-preview, room-card, device-strip, action-bar |
| Organisms | 11 | topbar, bottombar, stage, side-panel, side-panel-header, popover, modal, modal-header, modal-body, chat-input, room-list |
| Layout | 1 | mc-app（页面根容器 Grid 骨架） |

完整 HTML 范式和使用说明 → `references/component-catalog.md`

## 资源目录

> 注：本目录是 `trtc/room-builder/uikit/` 的一部分；`{skill_dir}` 指 `trtc/room-builder/`，因此下文所有 `{skill_dir}/uikit/...` 即本目录。

```
uikit/                                ← 本目录（trtc-room-builder 内部组件库）
├── README.md                         ← 本文件（内部说明，非 skill 触发入口）
├── scripts/
│   ├── generate-theme-overrides.py   ← 风格定制脚本（token 覆盖）
│   └── recolor-icons.py              ← SVG 图标品牌色批量替换
├── references/
│   ├── component-catalog.md          ← 60 个组件的完整目录与 HTML 范式
│   └── token-contract.md             ← ~100 个 Design Token 完整清单 + 暗色模式说明
└── assets/
    └── themes/meeting-classic/       ← 生产级组件库源文件
        ├── tokens.css                ← L1+L2 双层令牌定义（浅色）
        ├── tokens.dark.css           ← L1 暗色覆盖令牌
        ├── layout.css                ← 页面 Grid 骨架
        ├── index.css                 ← 汇总入口（@import 所有 CSS）
        ├── index.html                ← 完整会议页面参考实现（会议中）
        ├── pre-meeting.html          ← 完整进入页参考实现（会议前）
        ├── INTEGRATION.md            ← 框架接入指南
        ├── assets/                   ← 内置 SVG 图标集
        │   ├── icons/                ← 通用图标
        │   ├── contact/              ← 通讯录图标
        │   ├── members/              ← 成员管理图标
        │   ├── settings/             ← 设置面板图标
        │   ├── share/                ← 屏幕分享缩略图
        │   └── stage/                ← 视频舞台图标
        └── components/               ← 60 个组件 CSS 文件
            ├── atoms/                ← 25 个原子组件
            ├── molecules/            ← 24 个分子组件
            └── organisms/            ← 11 个组织组件
```
