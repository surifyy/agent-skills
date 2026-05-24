# TRTC Room UIKit · Design Token 契约

> 本文件定义组件库的 token 体系。生成代码时，**所有视觉属性必须通过 L2 别名令牌引用**，禁止硬编码颜色值、px 尺寸等。

---

## 双层 Token 结构

```
L1 皮肤令牌（--mc-*）
  ↓ 映射
L2 通用别名（--color-*、--space-*、--radius-* 等）
  ↓ 消费
组件 CSS
```

- **L1**：皮肤私有，带前缀（如 `--mc-color-primary`），只在 `tokens.css` 的 `[data-theme="mc"]` 下定义
- **L2**：无前缀通用名（如 `--color-primary`），组件 CSS 只使用 L2
- 切换皮肤时只需改 `data-theme`，L2 自动指向不同 L1

### 规则
1. 组件 CSS 中**禁止**直接引用 `--mc-*`
2. 组件 CSS 中**禁止**写 `#xxx` / `rgba(...)` / 固定 `px`（字号/间距/圆角/阴影）
3. 仅允许以下 inline style 用于数据驱动：
   - `background-image: url(...)` — 头像/图片
   - `--level: N%` — LevelBar 数据驱动
   - `--stage-off-avatar: url(...)` — Stage 关闭态头像

---

## L2 令牌完整清单

### 颜色 · Color（28 个）

| 令牌 | 默认值(mc) | 用途 |
|---|---|---|
| `--color-primary` | #3b82f6 | 品牌主色 |
| `--color-primary-hover` | #2563eb | 主色悬浮 |
| `--color-primary-strong` | #0958d9 | 深色文字 |
| `--color-primary-bg` | #e6f4ff | 浅底背景 |
| `--color-primary-ring` | rgba(59,130,246,.15) | 聚焦光环 |
| `--color-success` | #22c55e | 成功绿 |
| `--color-success-alt` | #facc15 | 渐变中段 |
| `--color-danger` | #ff4d4f | 危险红 |
| `--color-danger-strong` | #ef4444 | 深红 |
| `--color-danger-bg` | #fff1f0 | 危险浅底 |
| `--color-warning` | #f59e0b | 警告橙 |
| `--color-text` | #2b2b2b | 主要文字 |
| `--color-text-2` | #4a4a4a | 次要文字 |
| `--color-text-3` | #666666 | 三级文字 |
| `--color-muted` | #8c8c8c | 弱化/placeholder |
| `--color-text-on-primary` | #ffffff | 主色上的文字 |
| `--color-text-on-dark` | #d9d9d9 | 暗底文字 |
| `--color-icon` | #595959 | 图标默认色 |
| `--color-icon-muted` | #bfbfbf | 图标弱灰 |
| `--color-bg-base` | #ffffff | 主背景 |
| `--color-bg-hover` | #f5f5f5 | 悬浮背景 |
| `--color-bg-subtle` | #fafafa | 微弱背景 |
| `--color-bg-chat-bubble` | #f4f5f7 | 他人消息气泡 |
| `--color-bg-stage` | #f2f2f2 | 视频默认底 |
| `--color-bg-stage-off` | #2b2b2b | 关摄像头底 |
| `--color-bg-level` | #f0f0f0 | 音量条空底 |
| `--color-bg-preview` | #e4e9f5 | 布局缩略格 |
| `--color-bg-placeholder` | #d9d9d9 | 头像占位 |

### 边框 · Border（3 个）

| 令牌 | 默认值(mc) | 用途 |
|---|---|---|
| `--color-border` | #f0f0f0 | 分区线 |
| `--color-border-2` | #e6e6e6 | 表单/框架 |
| `--color-border-3` | #eaeaea | popover |

### 覆盖层 · Overlay（2 个）

| 令牌 | 默认值(mc) | 用途 |
|---|---|---|
| `--color-overlay-mask` | rgba(0,0,0,.4) | modal 遮罩 |
| `--color-overlay-badge` | rgba(0,0,0,.55) | 视频徽章底 |

### 字号 · Font Size（6 个）

| 令牌 | 默认值(mc) |
|---|---|
| `--font-xs` | 12px |
| `--font-sm` | 13px |
| `--font-base` | 13.5px |
| `--font-md` | 14px |
| `--font-lg` | 15px |
| `--font-xl` | 20px |

### 字重 · Font Weight（2 个）

| 令牌 | 默认值(mc) |
|---|---|
| `--font-weight-normal` | 400 |
| `--font-weight-medium` | 500 |

### 字体 · Font Family（2 个）

| 令牌 | 默认值(mc) |
|---|---|
| `--font-family` | -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif |
| `--font-family-mono` | tabular-nums |

### 行高 · Line Height（2 个）

| 令牌 | 默认值(mc) |
|---|---|
| `--line-normal` | 1.5 |
| `--line-tight` | 1.2 |

### 间距 · Space（15 个，2px 基准）

| 令牌 | 默认值(mc) |
|---|---|
| `--space-0` | 0 |
| `--space-0_5` | 2px |
| `--space-1` | 4px |
| `--space-1_5` | 6px |
| `--space-2` | 8px |
| `--space-2_5` | 10px |
| `--space-3` | 12px |
| `--space-3_5` | 14px |
| `--space-4` | 16px |
| `--space-4_5` | 18px |
| `--space-5` | 20px |
| `--space-5_5` | 22px |
| `--space-6` | 24px |
| `--space-6_5` | 26px |
| `--space-7` | 28px |

### 圆角 · Radius（11 个）

| 令牌 | 默认值(mc) | 用途 |
|---|---|---|
| `--radius-xs` | 2px | |
| `--radius-sm` | 4px | 按钮、小元素 |
| `--radius-md` | 6px | 中等元素 |
| `--radius-lg` | 8px | 卡片 |
| `--radius-xl` | 10px | 大卡片 |
| `--radius-2xl` | 14px | 弹窗 |
| `--radius-pill-sm` | 18px | 邀请按钮 |
| `--radius-pill` | 20px | 胶囊形 |
| `--radius-full` | 9999px | 正圆 |
| `--radius-bubble-them` | 4px 10px 10px 10px | 他人气泡 |
| `--radius-bubble-me` | 10px 4px 10px 10px | 自己气泡 |

### 阴影 · Shadow（4 个）

| 令牌 | 默认值(mc) | 用途 |
|---|---|---|
| `--shadow-pop` | 0 10px 30px rgba(0,0,0,.12) | 底部弹出 |
| `--shadow-pop-top` | 0 12px 32px rgba(0,0,0,.10) | 顶部弹出 |
| `--shadow-modal` | 0 20px 60px rgba(0,0,0,.25) | 模态弹窗 |
| `--shadow-focus-ring` | 0 0 0 2px var(--color-primary-ring) | 聚焦外环 |

### 图标 · Icon（8 个）

| 令牌 | 默认值(mc) |
|---|---|
| `--icon-size-xs` | 14px |
| `--icon-size-sm` | 16px |
| `--icon-size-md` | 18px |
| `--icon-size-lg` | 22px |
| `--icon-size-xl` | 26px |
| `--icon-stroke` | 1.6 |
| `--icon-stroke-strong` | 2 |
| `--icon-stroke-check` | 2.4 |

### 布局 · Layout（9 个）

| 令牌 | 默认值(mc) | 用途 |
|---|---|---|
| `--layout-min-width` | 1200px | 页面最小宽度（窄于此值出滚动条） |
| `--layout-topbar-h` | 60px | 顶栏高度 |
| `--layout-bottombar-h` | 80px | 底栏高度 |
| `--layout-side-w` | 320px | 侧栏宽度 |
| `--layout-side-footer-h` | 80px | 侧栏底部高度 |
| `--layout-modal-w` | 720px | 设置弹窗宽度 |
| `--layout-modal-invite-w` | 520px | 邀请弹窗宽度 |
| `--layout-modal-max-h` | 80vh | 弹窗最大高度 |
| `--layout-modal-min-h` | 380px | 弹窗最小高度 |
| `--layout-modal-nav-w` | 170px | 弹窗侧栏宽度 |

### 动效 · Motion（3 个）

| 令牌 | 默认值(mc) |
|---|---|
| `--duration-fast` | 0.15s |
| `--duration-base` | 0.2s |
| `--ease-standard` | ease |

### 层级 · Z-Index（6 个）

| 令牌 | 默认值(mc) |
|---|---|
| `--z-topbar` | 20 |
| `--z-side` | 25 |
| `--z-bottombar` | 30 |
| `--z-popover` | 50 |
| `--z-toppop` | 60 |
| `--z-modal` | 100 |

---

## 暗色模式

组件库内置 `tokens.dark.css`，通过 `[data-theme="mc"][data-mode="dark"]` 选择器激活。

### 使用方式
```html
<html data-theme="mc" data-mode="dark">
<head>
  <link rel="stylesheet" href="tokens.css" />
  <link rel="stylesheet" href="tokens.dark.css" />
</head>
```

### 运行时切换
```js
// 切换到暗色
document.documentElement.dataset.mode = 'dark';
// 切换回浅色
delete document.documentElement.dataset.mode;
```

### 原理
- `tokens.dark.css` 只覆盖 L1 令牌（`--mc-*`）
- L2 别名通过 `var()` 动态求值，自动跟随 L1 变化
- 无需修改任何组件 CSS

---

## 风格定制指南

### 换品牌色
修改 L1 中的 `--mc-color-primary` 系列（5 个值）即可全局换色：
```css
[data-theme="mc"] {
  --mc-color-primary:        #7c3aed;  /* 紫色 */
  --mc-color-primary-hover:  #6d28d9;
  --mc-color-primary-strong: #5b21b6;
  --mc-color-primary-bg:     #f5f3ff;
  --mc-color-primary-ring:   rgba(124, 58, 237, .15);
}
```

### 换圆角风格
修改 L1 中的 `--mc-radius-*` 系列：
```css
/* 更圆润 */
[data-theme="mc"] {
  --mc-radius-xs: 4px;
  --mc-radius-sm: 8px;
  --mc-radius-md: 12px;
  --mc-radius-lg: 16px;
  --mc-radius-xl: 20px;
  --mc-radius-2xl: 24px;
}
```

### 定制方式
创建一个 `overrides.css` 文件，在 `tokens.css` 之后引入：
```html
<link rel="stylesheet" href="themes/meeting-classic/tokens.css">
<link rel="stylesheet" href="overrides.css">
```
在 `overrides.css` 中只覆盖需要变更的 L1 令牌即可。
