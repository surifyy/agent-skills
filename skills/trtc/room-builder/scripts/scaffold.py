#!/usr/bin/env python3
"""
scaffold.py · TRTC Room Builder 页面脚手架生成器

根据场景类型生成一个包含正确 CSS 引用、基础 HTML 骨架和交互 JS 的起始页面。
AI 在此骨架上填充具体内容即可。

用法:
  python3 scaffold.py --scene meeting --title "果果的会议" --output ./output/
  python3 scaffold.py --scene voice-room --title "深夜电台" --output ./output/
  python3 scaffold.py --scene live-stream --title "直播间" --output ./output/
  python3 scaffold.py --scene one-on-one --title "视频通话" --output ./output/
  python3 scaffold.py --scene classroom --title "英语课堂" --output ./output/

参数:
  --scene     场景类型: meeting | voice-room | live-stream | one-on-one | classroom
  --title     页面标题
  --output    输出目录（会在其中生成 index.html）
  --theme-dir 主题资产相对路径（默认 themes/meeting-classic）
  --overrides 自定义覆盖 CSS 文件路径（可选）
"""

import argparse
import os
import sys

# ========== CSS 引入清单（按依赖顺序） ==========

TOKENS_AND_LAYOUT = [
    "tokens.css",
    "layout.css",
]

ATOMS = [
    "components/atoms/button.css",
    "components/atoms/avatar.css",
    "components/atoms/badge.css",
    "components/atoms/dot.css",
    "components/atoms/caret.css",
    "components/atoms/divider.css",
    "components/atoms/icon.css",
    "components/atoms/icon-slash.css",
    "components/atoms/input.css",
    "components/atoms/select.css",
    "components/atoms/label.css",
    "components/atoms/level-bar.css",
    "components/atoms/tag.css",
    "components/atoms/link.css",
    "components/atoms/spacer.css",
    "components/atoms/sr-only.css",
    "components/atoms/check.css",
]

MOLECULES = [
    "components/molecules/icon-button.css",
    "components/molecules/icon-button-caret.css",
    "components/molecules/toolbar-item.css",
    "components/molecules/search-input.css",
    "components/molecules/menu-item.css",
    "components/molecules/menu-section.css",
    "components/molecules/list-row.css",
    "components/molecules/list-row-actions.css",
    "components/molecules/chat-message.css",
    "components/molecules/chat-toolbar.css",
    "components/molecules/form-row.css",
    "components/molecules/info-row.css",
    "components/molecules/nav-item.css",
    "components/molecules/layout-preview-card.css",
    "components/molecules/layout-thumb.css",
    "components/molecules/signal-row.css",
    "components/molecules/user-pill.css",
    "components/molecules/lang-select.css",
]

ORGANISMS = [
    "components/organisms/popover.css",
    "components/organisms/modal.css",
    "components/organisms/modal-header.css",
    "components/organisms/modal-body.css",
    "components/organisms/side-panel.css",
    "components/organisms/side-panel-header.css",
    "components/organisms/stage.css",
    "components/organisms/topbar.css",
    "components/organisms/bottombar.css",
    "components/organisms/chat-input.css",
]

# ========== 场景骨架 ==========

SCENE_SKELETONS = {
    "meeting": {
        "css": TOKENS_AND_LAYOUT + ATOMS + MOLECULES + ORGANISMS,
        "body": """\
<div class="mc-app" id="app">

  <!-- ===== TOP BAR ===== -->
  <header class="ui-topbar">
    <div class="ui-topbar__left">
      <!-- TODO: toolbar-items (布局、网络等) -->
    </div>
    <div class="ui-topbar__center">
      <span class="ui-topbar__title">{title}<span class="ui-caret ui-caret--down"></span></span>
      <span class="ui-topbar__time">00:00</span>
    </div>
    <div class="ui-topbar__right">
      <!-- TODO: user-pill, lang-select -->
    </div>
  </header>

  <!-- ===== STAGE ===== -->
  <section class="ui-stage">
    <div class="ui-stage__frame" data-off-text="摄像头已关闭">
      <!-- TODO: 视频画面或头像占位 -->
    </div>
  </section>

  <!-- ===== SIDE PANEL ===== -->
  <aside class="ui-side-panel" id="side" data-active="">
    <div class="ui-side-panel__content" data-panel="members">
      <!-- TODO: 成员列表 -->
    </div>
    <div class="ui-side-panel__content" data-panel="chat">
      <!-- TODO: 聊天面板 -->
    </div>
  </aside>

  <!-- ===== BOTTOM BAR ===== -->
  <footer class="ui-bottombar">
    <div class="ui-bottombar__left">
      <!-- TODO: mic + cam icon-buttons -->
    </div>
    <div class="ui-bottombar__center">
      <!-- TODO: 功能按钮 -->
    </div>
    <div class="ui-bottombar__right">
      <button class="ui-btn ui-btn--end">结束房间</button>
    </div>
  </footer>

</div>""",
        "script": """\
/* meeting 交互骨架 */
const app = document.getElementById('app');
const side = document.getElementById('side');

function openPanel(name) {
  app.classList.add('is-panel-open');
  app.dataset.panel = name;
  side.classList.add('is-open');
  side.dataset.active = name;
}
function closePanel() {
  app.classList.remove('is-panel-open');
  app.dataset.panel = '';
  side.classList.remove('is-open');
  side.dataset.active = '';
}
document.querySelectorAll('[data-close-panel]').forEach(el => el.onclick = closePanel);

function closeAllPopovers() {
  document.querySelectorAll('.ui-popover.is-open').forEach(p => p.classList.remove('is-open'));
}
document.addEventListener('click', (e) => {
  if (!e.target.closest('.ui-popover') && !e.target.closest('[data-pop]')) closeAllPopovers();
});""",
    },

    "voice-room": {
        "css": TOKENS_AND_LAYOUT + ATOMS + MOLECULES[:11] + [
            "components/organisms/topbar.css",
            "components/organisms/bottombar.css",
            "components/organisms/chat-input.css",
        ],
        "body": """\
<div class="mc-app mc-app--voice-room" id="app">

  <!-- ===== TOP BAR ===== -->
  <header class="ui-topbar">
    <div class="ui-topbar__left">
      <span class="ui-topbar__title">{title}</span>
    </div>
    <div class="ui-topbar__center"></div>
    <div class="ui-topbar__right">
      <!-- TODO: 在线人数 + 用户信息 -->
    </div>
  </header>

  <!-- ===== 麦位区 ===== -->
  <section class="mc-seat-grid">
    <!-- TODO: 4x2 或 3x3 麦位网格，每格 avatar + 用户名 + 状态 -->
  </section>

  <!-- ===== 聊天消息区 ===== -->
  <section class="mc-chat-scroll">
    <!-- TODO: chat-message 列表 -->
  </section>

  <!-- ===== BOTTOM BAR ===== -->
  <footer class="ui-bottombar">
    <div class="ui-bottombar__left">
      <!-- TODO: 麦克风 icon-button -->
    </div>
    <div class="ui-bottombar__center">
      <!-- TODO: 举手、消息输入 -->
    </div>
    <div class="ui-bottombar__right">
      <button class="ui-btn ui-btn--end">离开</button>
    </div>
  </footer>

</div>""",
        "script": """\
/* voice-room 交互骨架 */
/* TODO: 麦位上下麦、麦克风切换 */""",
        "extra_css": """\
/* 语音房麦位网格 */
.mc-app--voice-room {
  grid-template-rows: var(--layout-topbar-h) 1fr auto var(--layout-bottombar-h);
  grid-template-areas: "topbar" "seats" "chat" "bottombar";
}
.mc-seat-grid {
  grid-area: seats;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  padding: var(--space-6);
  align-content: center;
  justify-items: center;
}
.mc-chat-scroll {
  grid-area: chat;
  overflow-y: auto;
  max-height: 200px;
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--color-border);
}""",
    },

    "live-stream": {
        "css": TOKENS_AND_LAYOUT + ATOMS + MOLECULES[:11] + [
            "components/organisms/topbar.css",
            "components/organisms/bottombar.css",
            "components/organisms/stage.css",
            "components/organisms/chat-input.css",
        ],
        "body": """\
<div class="mc-app mc-app--live" id="app">

  <!-- ===== TOP BAR ===== -->
  <header class="ui-topbar">
    <div class="ui-topbar__left">
      <!-- TODO: 主播信息 avatar + 昵称 -->
    </div>
    <div class="ui-topbar__center"></div>
    <div class="ui-topbar__right">
      <!-- TODO: 在线观众数 + 关闭按钮 -->
    </div>
  </header>

  <!-- ===== 主播视频区 ===== -->
  <section class="ui-stage">
    <div class="ui-stage__frame">
      <!-- TODO: 主播视频 -->
    </div>
  </section>

  <!-- ===== 连麦嘉宾小窗区 ===== -->
  <aside class="mc-guest-strip">
    <!-- TODO: 连麦嘉宾头像/小视频列表 -->
  </aside>

  <!-- ===== 互动区 ===== -->
  <section class="mc-live-chat">
    <!-- TODO: 弹幕式消息流 -->
  </section>

  <!-- ===== BOTTOM BAR ===== -->
  <footer class="ui-bottombar">
    <div class="ui-bottombar__left">
      <!-- TODO: 消息输入 -->
    </div>
    <div class="ui-bottombar__center">
      <!-- TODO: 连麦申请、礼物 -->
    </div>
    <div class="ui-bottombar__right">
      <!-- TODO: 分享、更多 -->
    </div>
  </footer>

</div>""",
        "script": """\
/* live-stream 交互骨架 */
/* TODO: 连麦申请流程、弹幕滚动 */""",
        "extra_css": """\
/* 直播连麦布局 */
.mc-app--live {
  grid-template-rows: var(--layout-topbar-h) 1fr auto auto var(--layout-bottombar-h);
  grid-template-areas: "topbar" "stage" "guests" "chat" "bottombar";
}
.mc-guest-strip {
  grid-area: guests;
  display: flex;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  overflow-x: auto;
}
.mc-live-chat {
  grid-area: chat;
  max-height: 180px;
  overflow-y: auto;
  padding: var(--space-2) var(--space-4);
}""",
    },

    "one-on-one": {
        "css": TOKENS_AND_LAYOUT + ATOMS[:8] + [
            "components/molecules/icon-button.css",
            "components/organisms/stage.css",
            "components/organisms/bottombar.css",
        ],
        "body": """\
<div class="mc-app mc-app--call" id="app">

  <!-- ===== 对方视频（全屏） ===== -->
  <section class="ui-stage mc-stage--fullscreen">
    <div class="ui-stage__frame" data-off-text="摄像头已关闭">
      <!-- TODO: 对方视频 -->
    </div>
    <!-- 自己小窗 -->
    <div class="mc-pip">
      <!-- TODO: 自己视频 / avatar -->
    </div>
  </section>

  <!-- ===== 底部控制栏（浮于视频上） ===== -->
  <footer class="ui-bottombar mc-bottombar--floating">
    <div class="ui-bottombar__center">
      <!-- TODO: 麦克风 | 视频 | 扬声器 | 挂断 -->
    </div>
  </footer>

  <!-- 通话计时 -->
  <div class="mc-call-timer">
    <span class="ui-badge">00:00</span>
  </div>

</div>""",
        "script": """\
/* one-on-one 交互骨架 */
/* TODO: 麦/摄切换、挂断逻辑 */""",
        "extra_css": """\
/* 1v1 通话布局 */
.mc-app--call {
  grid-template-rows: 1fr auto;
  grid-template-areas: "stage" "bottombar";
}
.mc-stage--fullscreen { grid-area: stage; position: relative; }
.mc-pip {
  position: absolute;
  bottom: var(--space-4);
  right: var(--space-4);
  width: 120px;
  height: 160px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-pop);
  background: var(--color-bg-stage-off);
}
.mc-bottombar--floating {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: transparent;
  border-top: none;
}
.mc-call-timer {
  position: absolute;
  top: var(--space-4);
  left: 50%;
  transform: translateX(-50%);
  z-index: var(--z-toppop);
}""",
    },

    "classroom": {
        "css": TOKENS_AND_LAYOUT + ATOMS + MOLECULES + ORGANISMS,
        "body": """\
<div class="mc-app" id="app">

  <!-- ===== TOP BAR ===== -->
  <header class="ui-topbar">
    <div class="ui-topbar__left">
      <span class="ui-topbar__title">{title}</span>
    </div>
    <div class="ui-topbar__center">
      <span class="ui-topbar__time">00:00</span>
    </div>
    <div class="ui-topbar__right">
      <!-- TODO: 老师信息 + 学生人数 -->
    </div>
  </header>

  <!-- ===== 老师画面/屏幕共享 ===== -->
  <section class="ui-stage">
    <div class="ui-stage__frame">
      <!-- TODO: 老师视频或屏幕共享画面 -->
    </div>
  </section>

  <!-- ===== SIDE PANEL ===== -->
  <aside class="ui-side-panel" id="side" data-active="">
    <div class="ui-side-panel__content" data-panel="students">
      <!-- TODO: 学生列表（含举手状态） -->
    </div>
    <div class="ui-side-panel__content" data-panel="chat">
      <!-- TODO: 课堂聊天 -->
    </div>
  </aside>

  <!-- ===== BOTTOM BAR ===== -->
  <footer class="ui-bottombar">
    <div class="ui-bottombar__left">
      <!-- TODO: 麦克风 + 视频 -->
    </div>
    <div class="ui-bottombar__center">
      <!-- TODO: 共享屏幕 | 举手 | 学生列表 | 聊天 -->
    </div>
    <div class="ui-bottombar__right">
      <button class="ui-btn ui-btn--end">离开课堂</button>
    </div>
  </footer>

</div>""",
        "script": """\
/* classroom 交互骨架 — 与 meeting 类似 */
const app = document.getElementById('app');
const side = document.getElementById('side');

function openPanel(name) {
  app.classList.add('is-panel-open');
  side.classList.add('is-open');
  side.dataset.active = name;
}
function closePanel() {
  app.classList.remove('is-panel-open');
  side.classList.remove('is-open');
  side.dataset.active = '';
}
document.querySelectorAll('[data-close-panel]').forEach(el => el.onclick = closePanel);""",
    },

    "pre-meeting": {
        "css": TOKENS_AND_LAYOUT + ATOMS + [
            "components/atoms/spinner.css",
            "components/atoms/password-input.css",
        ] + [
            "components/molecules/icon-button.css",
            "components/molecules/toolbar-item.css",
            "components/molecules/search-input.css",
            "components/molecules/form-row.css",
            "components/molecules/info-row.css",
            "components/molecules/user-pill.css",
            "components/molecules/lang-select.css",
            "components/molecules/tree-item.css",
            "components/molecules/camera-preview.css",
            "components/molecules/room-card.css",
            "components/molecules/device-strip.css",
            "components/molecules/action-bar.css",
        ] + [
            "components/organisms/topbar.css",
            "components/organisms/modal.css",
            "components/organisms/modal-header.css",
            "components/organisms/modal-body.css",
            "components/organisms/room-list.css",
        ],
        "body": """\
<div class="mc-lobby" id="lobby" data-view="history">

  <!-- ===== TOP BAR ===== -->
  <header class="ui-topbar">
    <div class="ui-topbar__left">
      <!-- TODO: toolbar-items -->
    </div>
    <div class="ui-topbar__center"></div>
    <div class="ui-topbar__right">
      <!-- TODO: user-pill, lang-select -->
    </div>
  </header>

  <!-- ===== MAIN CONTENT ===== -->
  <main class="mc-lobby__main">
    <div class="mc-lobby__logo">
      <span class="mc-lobby__logo-text">{title}</span>
    </div>

    <div class="mc-lobby__content">
      <!-- 摄像头预览 -->
      <div class="mc-lobby__preview-area">
        <div class="ui-camera-preview is-off">
          <div class="ui-camera-preview__placeholder">
            <!-- TODO: 头像图标 -->
            <span class="ui-camera-preview__hint">暂无摄像画面</span>
          </div>
        </div>

        <div class="mc-lobby__controls">
          <div class="ui-device-strip">
            <!-- TODO: mic + cam 设备检测项 -->
          </div>
          <div class="ui-action-bar">
            <button class="ui-action-bar__btn ui-action-bar__btn--secondary">加入房间</button>
            <button class="ui-action-bar__btn ui-action-bar__btn--primary">新建房间</button>
            <button class="ui-action-bar__btn ui-action-bar__btn--secondary">预定房间</button>
          </div>
        </div>
      </div>

      <!-- 历史房间列表 -->
      <div class="ui-room-list" id="room-list">
        <div class="ui-room-list__header">
          <a class="ui-room-list__link">历史房间 →</a>
        </div>
        <div class="ui-room-list__body">
          <!-- TODO: room-card 列表 -->
        </div>
      </div>
    </div>
  </main>
</div>""",
        "script": """\
/* pre-meeting 交互骨架 */
function openModal(id) { document.getElementById(id).classList.add('is-open'); }
function closeModal(id) { document.getElementById(id).classList.remove('is-open'); }
document.querySelectorAll('[data-close-modal]').forEach(el => {
  el.onclick = () => closeModal(el.dataset.closeModal);
});
document.querySelectorAll('.ui-modal').forEach(m => {
  m.addEventListener('click', (e) => { if (e.target === m) m.classList.remove('is-open'); });
});""",
        "extra_css": """\
/* mc-lobby 布局 */
.mc-lobby {
  width: 100vw;
  height: 100vh;
  display: grid;
  grid-template-rows: var(--layout-topbar-h) 1fr;
  background: linear-gradient(135deg, #f0f2f8 0%, #e8ecf4 50%, #f5f3f0 100%);
  position: relative;
}
.mc-lobby__main {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-5);
  padding: var(--space-6);
}
.mc-lobby__logo { display: flex; align-items: center; gap: var(--space-2); }
.mc-lobby__logo-text { font-size: var(--font-xl); font-weight: var(--font-weight-medium); color: var(--color-primary); }
.mc-lobby__content { display: flex; align-items: flex-start; gap: var(--space-6); }
.mc-lobby__preview-area { display: flex; flex-direction: column; align-items: center; gap: var(--space-4); }
.mc-lobby__controls { display: flex; flex-direction: column; align-items: center; gap: var(--space-3); }
.mc-lobby[data-view="default"] #room-list { display: none; }""",
    },
}


def build_css_links(css_files, theme_dir, overrides=None):
    """Generate <link> tags for CSS files."""
    lines = []
    for f in css_files:
        lines.append('<link rel="stylesheet" href="{}/{}" />'.format(theme_dir, f))
    if overrides:
        lines.append('<link rel="stylesheet" href="{}" />'.format(overrides))
    return "\n".join(lines)


def build_html(scene, title, theme_dir, overrides=None):
    """Build complete HTML page."""
    config = SCENE_SKELETONS[scene]

    css_links = build_css_links(config["css"], theme_dir, overrides)
    body = config["body"].format(title=title)
    script = config["script"]
    extra_css = config.get("extra_css", "")

    parts = [
        '<!DOCTYPE html>',
        '<html lang="zh-CN" data-theme="mc">',
        "<head>",
        '<meta charset="UTF-8" />',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />',
        "<title>{}</title>".format(title),
        "",
        "<!-- TRTC Room UIKit CSS -->",
        css_links,
        "</head>",
        "<body>",
        "",
        body,
    ]

    if extra_css:
        parts.append("")
        parts.append("<style>")
        parts.append(extra_css)
        parts.append("</style>")

    parts.append("")
    parts.append("<script>")
    parts.append(script)
    parts.append("</script>")
    parts.append("")
    parts.append("</body>")
    parts.append("</html>")

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="TRTC Room Builder - Page scaffold generator"
    )
    parser.add_argument(
        "--scene",
        required=True,
        choices=list(SCENE_SKELETONS.keys()),
        help="Scene type",
    )
    parser.add_argument("--title", default="TRTC Room", help="Page title")
    parser.add_argument("--output", default=".", help="Output directory")
    parser.add_argument(
        "--theme-dir",
        default="themes/meeting-classic",
        help="Relative path to theme assets",
    )
    parser.add_argument("--overrides", default=None, help="Custom override CSS path")

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    html = build_html(args.scene, args.title, args.theme_dir, args.overrides)

    output_path = os.path.join(args.output, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("Generated: {} (scene: {})".format(output_path, args.scene))
    print("Theme dir: {}".format(args.theme_dir))
    if args.overrides:
        print("Overrides: {}".format(args.overrides))


if __name__ == "__main__":
    main()
