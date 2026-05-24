# meeting-classic · 开发者接入指南

> 本指南面向**业务前端开发者**（React / Vue / Svelte / 原生 HTML 等）。
> 如果你是皮肤维护者要处理新 demo，请改读 [skills/demo-to-theme/SKILL.md](../../skills/demo-to-theme/SKILL.md)。

---

## 一分钟接入

### Step 1 · 引入 CSS

```html
<!DOCTYPE html>
<html lang="zh-CN" data-theme="mc">
<head>
  <link rel="stylesheet" href="path/to/themes/meeting-classic/tokens.css">
  <!-- 然后按顺序引入所有 components/*.css 和 layout.css
       完整顺序参考本目录下 index.html 头部的 link 列表 -->
</head>
```

**关键约束**：

1. `<html data-theme="mc">` 必须设置（缩写 `mc` = meeting-classic）
2. `tokens.css` 必须先于 components 加载
3. 多皮肤共存时，`<html data-theme="...">` 决定当前生效皮肤

### Step 2 · 复用组件 HTML

打开本目录下 `index.html`，搜索你需要的界面元素，复制对应 HTML 结构到你的项目。

### Step 3 · 用框架的 class 绑定语法切换 `.is-*` 状态

参考下面"框架接入"。

---

## 二、框架接入

### React / Next.js

```jsx
// _app.tsx 或 layout.tsx 全局引入
import 'themes/meeting-classic/tokens.css';
// ... 引入所有 components CSS

// 根布局设 data-theme
<html lang="zh-CN" data-theme="mc">

// 业务组件
function CamButton() {
  const [isOff, setIsOff] = useState(false);
  return (
    <div
      className={`ui-icon-button ui-icon-button--with-caret ${isOff ? 'is-off' : ''}`}
      onClick={() => setIsOff(!isOff)}
    >
      <span className="ui-icon-button__iconrow">
        <span className="ui-icon-button__icon">
          <span className="ui-icon-slot">
            <svg className="ui-icon ui-icon--lg ui-icon--inherit" viewBox="0 0 24 24"
                 fill="none" stroke="currentColor" strokeWidth="1.6"
                 strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="6" width="13" height="12" rx="2"/>
              <path d="M16 10l5-3v10l-5-3z"/>
            </svg>
            <span className="ui-icon-slash" aria-hidden="true"></span>
          </span>
        </span>
      </span>
      <span className="ui-icon-button__label">视频</span>
    </div>
  );
}
```

### Vue 3

```vue
<script setup>
import { ref } from 'vue';
const isOff = ref(false);
</script>

<template>
  <div :class="['ui-icon-button', 'ui-icon-button--with-caret', { 'is-off': isOff }]"
       @click="isOff = !isOff">
    <span class="ui-icon-button__iconrow">
      <span class="ui-icon-button__icon">
        <span class="ui-icon-slot">
          <svg class="ui-icon ui-icon--lg ui-icon--inherit" viewBox="0 0 24 24"
               fill="none" stroke="currentColor" stroke-width="1.6"
               stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="6" width="13" height="12" rx="2"/>
            <path d="M16 10l5-3v10l-5-3z"/>
          </svg>
          <span class="ui-icon-slash" aria-hidden="true"></span>
        </span>
      </span>
    </span>
    <span class="ui-icon-button__label">视频</span>
  </div>
</template>
```

### 原生 HTML / Vanilla JS

```html
<div class="ui-icon-button ui-icon-button--with-caret" id="cam-btn">
  <!-- 同上结构 -->
</div>

<script>
  document.getElementById('cam-btn').addEventListener('click', e => {
    e.currentTarget.classList.toggle('is-off');
  });
</script>
```

---

## 三、状态类速查（最重要！）

**所有运行时态都通过 `.is-*` class 切换，禁止用 inline style。**

| 类 | 用途 |
|---|---|
| `.is-active` | 激活/选中（nav 当前页、tab 选中、popover 打开） |
| `.is-open` | 展开/显示（抽屉、折叠面板） |
| `.is-selected` | 持久选中态（菜单选项） |
| `.is-off` | 关闭功能（关麦/关摄像头，触发斜杠图标） |
| `.is-on` | 开启 |
| `.is-disabled` | 不可交互 |
| `.is-loading` | 加载中 |
| `.is-hidden` / `.is-show` | 显隐控制 |
| `.is-muted` | 静音/弱化 |
| `.is-interactive` | 交互可点击的视觉提示 |
| `.is-truncate` | 单行省略 |
| `.is-warning` | 警告 |

---

## 四、组件 HTML 范式

完整组件清单与 HTML 范式：[shared/component-schema.md](../../shared/component-schema.md)

可执行样板：[index.html](./index.html)

主要组件分类：

- **Atoms（17）**：ui-btn / ui-avatar / ui-badge / ui-icon / ui-icon-slot+slash / ui-input / …
- **Molecules（18）**：ui-icon-button / ui-search-input / ui-menu-item / ui-list-row / …
- **Organisms（10）**：ui-popover / ui-modal / ui-side-panel / ui-stage / ui-topbar / ui-bottombar / …

---

## 五、CSS 变量速查（L2 令牌）

业务代码可以直接用的 CSS 变量（不带皮肤前缀）：

```css
.my-page-section {
  background: var(--color-bg-base);
  color: var(--color-text-1);
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-6);
  font-size: var(--font-md);
  box-shadow: var(--shadow-md);
}
```

完整清单（约 100 个）：[shared/token-schema.md](../../shared/token-schema.md)

**禁止**直接引用 `--mc-*` 前缀的 L1 令牌（皮肤私有，跨皮肤切换会失效）。

---

## 六、运行时换肤

```js
// 加载多套皮肤后切换
document.documentElement.dataset.theme = 'mc';   // 当前皮肤
document.documentElement.dataset.theme = 'md';   // 切换到暗色（如已实现）
```

```jsx
// React Hook
function useTheme(initial = 'mc') {
  const [theme, setTheme] = useState(initial);
  useEffect(() => { document.documentElement.dataset.theme = theme; }, [theme]);
  return [theme, setTheme];
}
```

---

## 七、FAQ

### Q1: 我能新加一个颜色吗？
不能在业务代码里写 `#xxx` 或 `rgb(...)`。如果现有 token 不够用，向皮肤维护者申请新增 L2 token（见 02-tokenize.md 流程）。

### Q2: 我能改组件的 padding 吗？
不能直接改 `components/*.css`。三种合规做法：
1. 改 token（影响所有用到的地方，慎用）
2. 用现有变体（如 `ui-btn--sm`）
3. 用页面工具类 `.mc-xxx` 包一层（仅限页面专属调整）

### Q3: 我想做个新的图标按钮变体怎么办？
先看 `shared/component-schema.md` 是否已有对应变体。没有的话，向皮肤维护者申请扩展 schema，不要私自加 `ui-*` class。

### Q4: 直接复制组件 CSS 到我的 styled-component 行吗？
**强烈不建议**。这样会使皮肤升级（如修复某个 bug）无法同步过来。请直接 link CSS 文件，业务代码只用 class。

### Q5: 我的 React 组件库要不要把 ui-btn 包成 `<Button />`？
可以，但建议**透传 className**让消费方决定变体：
```jsx
function Button({ variant = 'primary', size, className = '', children, ...rest }) {
  const cls = ['ui-btn', `ui-btn--${variant}`, size && `ui-btn--${size}`, className]
                .filter(Boolean).join(' ');
  return <button className={cls} {...rest}>{children}</button>;
}
```

### Q6: 同时支持多套皮肤怎么做？
全部 `index.css` 都 link，运行时改 `<html data-theme="x">`。所有 L2 令牌名一致（schema 强制），切换时全量自动同步。

### Q7: 不引入完整 index.css 行吗？只想用某几个组件
可以。最小集合：
```html
<link rel="stylesheet" href=".../tokens.css">  <!-- 必须 -->
<link rel="stylesheet" href=".../components/atoms/button.css">  <!-- 按需 -->
<link rel="stylesheet" href=".../components/atoms/icon.css">
```

但要保证所依赖的 atoms 都引入（见各文件头注释里的"依赖"声明）。

---

## 八、与皮肤维护者的协作流程

发现问题或需要新功能：

1. 在 `shared/component-schema.md` 或 `shared/token-schema.md` 提 issue
2. 皮肤维护者按 [03-componentize.md](../../skills/demo-to-theme/03-componentize.md) / [02-tokenize.md](../../skills/demo-to-theme/02-tokenize.md) 流程升级
3. 升级后 schema version bump，业务侧拉新版即可

---

## 九、本皮肤元数据

| 项 | 值 |
|---|---|
| 皮肤名 | meeting-classic |
| 前缀 | `mc` |
| `data-theme` | `mc` |
| 风格 | 浅色经典视频会议风 |
| 源 demo | [_source/meeting.html](./_source/meeting.html) |
| 完整说明 | [README.md](./README.md) |
