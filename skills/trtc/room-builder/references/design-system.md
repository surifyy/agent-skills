# Room UI Design System (Fallback Spec)

> **Purpose:** When none of the 12 ready-made templates fits, follow this spec to generate a NEW Room/Conferencing UI matching the same quality bar. Every rule is **derived from analyzing all 12 reference templates** — proven defaults, not invented.

---

## 0. The 6 Non-Negotiable Rules

1. **Tech stack is fixed.** Tailwind v4 browser build + Lucide icons + Plus Jakarta Sans (UI) + a secondary body font. No exceptions.
2. **Outer shell is always a rounded container.** `max-w-[1380px]` to `max-w-[1400px]`, `rounded-3xl`, `shadow-xl` or `shadow-2xl`, single screen, height ~820–880px.
3. **Three-column information architecture.** Left icon-rail (68–72px) + main video area (flex-1) + right contextual panel (300–340px). Drop one when the design demands, never invent a fourth.
4. **Round buttons + dark-glass overlay** for in-video controls. `rounded-full`, `bg-white/20`, `backdrop-blur-sm`, `w-11 h-11` to `w-12 h-12`. Hang-up is always a red `bg-red-500` 12–14px wider than its siblings.
5. **Accent color is one bold hue.** Pick ONE primary color (`--color-primary`) and a complementary danger red. Never use more than 3 functional hues.
6. **Portraits are real photos** from the sibling `people-library` skill. Never cartoon avatars, never letter monograms (emergency fallback only).
7. **Minimum viewport width is 1200px.** All pages must set `min-width: 1200px` on the outer container (or body). When the browser is narrower than 1200px, horizontal scrollbar appears — content never compresses or reflows. Implement via:
   ```css
   body { min-width: 1200px; }
   @media (max-width: 1199px) { html { overflow-x: auto; } }
   ```

---

## 1. Tech-Stack Boilerplate

Every Room UI page MUST start with this exact head:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><!-- Page title --></title>
  <link rel="preconnect" href="https://unpkg.com" />
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
  <script src="https://unpkg.com/@fortawesome/fontawesome-free@6.7.2/js/all.min.js"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>* { scrollbar-width: none; }</style>
</head>
```

End with:
```html
<script>if (window.lucide) lucide.createIcons();</script>
```

This is **mandatory**. Lucide icons render as `<i data-lucide="...">` placeholders until this call fires.

---

## 2. Typography System

### 2.1 Font Pairings

| Persona / Brand mood | Display font | Body font | Templates |
|---|---|---|---|
| **Default modern SaaS** | Plus Jakarta Sans | DM Sans | 01, 03, 09, 12 |
| **Default neutral** | Plus Jakarta Sans | Plus Jakarta Sans | 04, 05, 06, 08 |
| **Editorial / pro-services** | Plus Jakarta Sans | Source Serif 4 | 02, 07 |
| **Creative startup** | Syne | DM Sans | 03, 09 |
| **Premium / luxury** | Fraunces or Playfair | DM Sans | 10, 11 |

Always use `https://fonts.googleapis.cn/css2?family=...` CDN.

### 2.2 Font-size Scale

| Token | Tailwind | Use case |
|---|---|---|
| Hero title | `text-2xl` | Top-bar page title |
| Section heading | `text-lg` | Panel titles |
| Subsection | `text-base` | Card-block titles |
| Body | `text-sm` | Chat messages, names |
| Helper | `text-xs` | Timestamps, role badges |
| Micro | `text-[10px]` to `text-[11px]` | Badges, tags |

### 2.3 Font-weight Conventions
- Page/panel titles → `font-bold` (700)
- Names, sub-titles → `font-semibold` (600)
- Body → `font-medium` (500) or default
- Labels / metadata → default with reduced color

### 2.4 Theme Block Pattern

```html
<style type="text/tailwindcss">
@theme {
  --font-main: 'Plus Jakarta Sans', sans-serif;
  --font-body: 'DM Sans', sans-serif;
}
body { font-family: var(--font-body); }
</style>
```

Apply `style="font-family:var(--font-main)"` to title elements.

---

## 3. Color System

### 3.1 Token Anatomy

```css
@theme {
  --color-primary: #38BDF8;          /* one bold hue */
  --color-primary-dark: #0EA5E9;     /* hover/pressed */
  --color-primary-light: #EEF1FE;    /* tinted bg */
  --color-card: #FFFFFF;             /* main surface */
  --color-sidebar-bg: #F8FAFF;       /* tinted sidebar */
  --color-danger: #FF3B30;           /* hang-up + errors */
  --color-text-main: #1A1235;
  --color-text-muted: #6B6490;
}
```

### 3.2 Approved Brand Hues (pick ONE)

| Hue family | Primary | Dark | Light tint | Templates |
|---|---|---|---|---|
| Sky blue | `#38BDF8` | `#0EA5E9` | `#EEF1FE` | 01 |
| Indigo blue | `#4F6EF7` | `#3B58E0` | `#EEF1FE` | 12 |
| Royal blue | `#2563FF` | `#1D4FD0` | `#E8F0FF` | 04 |
| Forest green | `#2D6A4F` | `#1B4332` | `#D8F3DC` | 02, 07 |
| Mint green | `#00C48A` | `#00A876` | `#D8F4EC` | 05 |
| Teal | `#00C9A7` | `#00A88B` | `#D8F4EC` | 06 |
| Purple | `#7C5CFC` | `#5A3AD8` | `#F4F1FF` | 03 |
| Indigo violet | `#6366F1` | `#4F4DDB` | `#EEF1FE` | 10 |
| Antique gold | `#C9A96E` | `#A98D4E` | `#C9A96E33` | 08 |
| Terracotta | `#E07A5F` | `#C25E45` | `#FFF2E8` | 11 |
| Aurora gradient | `linear-gradient(135deg,#667eea 0%,#764ba2 50%,#00d2ff 100%)` | — | — | 09 |

### 3.3 Background Strategy

**a) Soft solid** — `bg-neutral-50`, `bg-slate-100`, `bg-[#F4F4F6]`, `bg-[#FFF8F0]`. Calm, default. (02, 04, 07, 11, 12)

**b) Pastel diagonal gradient** — friendly. (01, 03, 10)
```html
<body style="background: linear-gradient(135deg, #E8EAFF 0%, #D5E0FF 40%, #E0E7FF 100%);">
```

**c) Bold solid** — when brand color IS the bg. (05 uses `bg-[#00C48A]`)

**d) Dark animated aurora** — premium. (08, 09)
```html
<style>
  .aurora-bg {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 30%, #1a1a3e 50%, #0f3460 100%);
    background-size: 300% 300%;
    animation: auroraShift 15s ease-in-out infinite;
  }
  @keyframes auroraShift {
    0%,100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
  }
</style>
```

### 3.4 Functional Color Conventions

| Meaning | Color | Where it appears |
|---|---|---|
| Active / on | `--color-primary` | Active nav, send btn, mic-on |
| Recording | `bg-red-500 animate-pulse` | Top-right REC dot |
| Hang up | `bg-red-500` | Larger circular toolbar btn |
| Mic muted | `bg-red-500/20` + `text-red-400` icon | Mic-off state |
| Online / Active | `bg-green-500` | Status dot bottom-right of avatar |
| Raised hand / Wait | `bg-yellow-500` | Status dot or yellow icon |
| Offline / Invited | `bg-gray-500` | Status dot |

---

## 4. Layout & Grid System

### 4.1 Outer Shell

```html
<body class="min-h-screen flex items-center justify-center p-6 [bg-...]">
  <div class="w-full max-w-[1400px] h-[840px] bg-card rounded-3xl shadow-2xl overflow-hidden flex">
    <!-- 3 columns inside -->
  </div>
</body>
```

Variants:
- Full-screen immersive (07, 08, 09, 11): drop centering and `rounded-3xl`, use `h-screen overflow-hidden`, add `fixed bottom-5` toolbar.
- Inline scroll-flow (04, 05, 06): `mx-auto` centering, allow page scroll.

### 4.2 Three Columns

| Column | Width | Purpose |
|---|---|---|
| Left icon rail | `w-[68px]` to `w-[72px]` | Logo + 5–6 nav icons + bottom avatar |
| Main content | `flex-1` | Top bar + video stage + (optional) bottom row |
| Right side panel | `w-[300px]` to `w-[340px]` | Chat / participants / notes |

### 4.3 Inner Spacing

| Concept | Tailwind |
|---|---|
| Outer page padding | `p-6` or `p-8` |
| Panel padding | `p-4` (compact) / `p-5` |
| Section vertical gap | `gap-4` or `gap-5` |
| Card padding | `p-4` / `p-5` |
| Pill padding | `px-2.5 py-1` to `px-3 py-1.5` |

### 4.4 Border Radius Scale

| Element | Tailwind | Px |
|---|---|---|
| Outer shell | `rounded-3xl` | 24 |
| Video tile, large card | `rounded-2xl` | 16 |
| Inline card / chat input | `rounded-xl` | 12 |
| Square button | `rounded-lg` | 8 |
| Pill / badge / avatar | `rounded-full` | ∞ |

### 4.5 Shadow Scale

| Element | Class |
|---|---|
| Outer shell | `shadow-xl` or `shadow-2xl` |
| Tinted | `shadow-2xl shadow-primary/10` |
| Card hover | `hover:shadow-lg` + `transform: translateY(-2px)` |
| Floating toolbar | `shadow-xl shadow-primary/30` |
| Hang-up | `shadow-lg shadow-red-500/30` |

---

## 5. Iconography

- Library: **Lucide** (always). FontAwesome only for brand logos (Google "G", etc.).
- Usage: `<i data-lucide="video" class="w-5 h-5 text-white"></i>`

| Context | Icon size | Container |
|---|---|---|
| Toolbar control | `w-5 h-5` | `w-11 h-11` or `w-12 h-12` round |
| Sidebar nav icon | `w-5 h-5` | `w-10 h-10` rounded-xl |
| Inline action | `w-4 h-4` | (no container) |
| Pill inline | `w-3 h-3` to `w-3.5 h-3.5` | flex inline |
| Status mic-off mini | `w-2 h-2` to `w-2.5 h-2.5` | 14–16px round dot |

Standard icon names by function:

| Function | Icon |
|---|---|
| Camera on / off | `video` |
| Mic on / off | `mic` / `mic-off` |
| Hang up | `phone-off` |
| Screen share | `monitor-up` / `monitor` |
| Raise hand | `hand` |
| Chat | `message-square` / `message-circle` |
| Participants | `users` |
| Settings | `settings` |
| More | `more-horizontal` / `ellipsis` |
| Send | `send` |
| Pin | `pin` |
| Maximize | `maximize-2` |
| Add user | `user-plus` |
| Calendar | `calendar` |
| Notification | `bell` |
| Search | `search` |
| Volume | `volume-2` / `volume-x` |
| Encrypted | `shield-check` |

---

## 6. Component Patterns (the "vocabulary")

### 6.1 `<NavRail>` — Left icon column
- 68–72px wide, `bg-sidebar-bg` or `bg-white border-r border-neutral-100`
- `flex flex-col items-center py-5 gap-2`
- Top: 40×40 brand logo block, gradient bg, rounded-xl
- Middle: 5–6 icon buttons, 40×40 rounded-xl
- Active: `bg-primary text-white` OR `bg-white shadow-md text-primary`
- Bottom: avatar (`mt-auto`) — 40×40 rounded-full ring-2

### 6.2 `<TopBar>` — Header row
- `px-6 py-4 flex items-center justify-between`
- Left: optional back btn + title (`text-lg font-bold`) + subtitle (`text-xs text-neutral-400`)
- Right: search, bell w/ red dot, user chip

### 6.3 `<VideoStage>` — Hero speaker tile
```html
<div class="relative rounded-2xl overflow-hidden bg-neutral-800 h-[380px]">
  <img src="..." class="w-full h-full object-cover" />
  <!-- top-left avatar group, top-right REC, left vol slider, bottom toolbar -->
</div>
```
Always `object-cover`. Add `bg-gradient-to-t from-black/30 via-transparent to-transparent` overlay if text on top.

### 6.4 `<ToolbarOverlay>` — Bottom controls
5–7 round glass buttons. Hang-up is RED + larger. See `component-library.md` D1.

### 6.5 `<ParticipantTile>` — Grid cell or thumbnail
Two flavors: large grid cell w/ name pill + mic state, small thumbnail w/ truncated name.

### 6.6 `<AvatarGroup>` — Stacked overlapping
`flex -space-x-2` + `border-2 border-white` on each avatar + optional `+N` chip.

### 6.7 `<StatusDot>` — On avatar
green=on · red=muted · yellow=raised hand · gray=offline.

### 6.8 `<ChatPanel>` — Right messaging
Header w/ tabs → message list → input row.

### 6.9 `<MessageBubble>`
- Other: left-aligned, `bg-neutral-100`, `rounded-tl-sm` (asymmetric corner)
- Self: right-aligned, `bg-primary text-white`, `rounded-tr-sm`

### 6.10 `<RolePill>` / `<StatusBadge>`
`text-[10px] font-semibold px-2.5 py-1 rounded-full bg-primary/10 text-primary`

### 6.11 `<SubtitleBar>` — Captions
Either inline below video or full-width bottom overlay (`bg-gray-900/80 backdrop-blur-sm`).

### 6.12 `<WaveformBars>` — Animated audio
7–20 vertical bars, varied heights, `bg-primary/30..100`, optional `animate-bounce` w/ staggered delays.

### 6.13 `<VolumeSlider>` — Vertical, on left edge
`w-1.5 h-28 bg-white/20 rounded-full` rail + filled portion + thumb.

### 6.14 `<RecordingBadge>` — Top-right corner
`bg-black/60 backdrop-blur-sm rounded-full` + `bg-red-500 animate-pulse` dot + monospace timer.

### 6.15 `<SpeakerInfoCard>` — Top-left identifier
Glass card with avatar + role label + name.

---

## 7. Animation Library

```css
@keyframes pulse-red {
  0%,100% { opacity: 1; }
  50%     { opacity: 0.4; }
}
.animate-pulse-red { animation: pulse-red 1.5s ease-in-out infinite; }

@keyframes speakerGlow {
  0%,100% { box-shadow: 0 0 0 0 rgba(<primary-rgb>, 0.4); }
  50%     { box-shadow: 0 0 0 6px rgba(<primary-rgb>, 0); }
}
.speaking { animation: speakerGlow 2.5s ease-in-out infinite; }

@keyframes auroraShift {
  0%,100% { background-position: 0% 50%; }
  50%     { background-position: 100% 50%; }
}
.aurora-bg { animation: auroraShift 15s ease-in-out infinite; }

.tilt-card {
  transform: rotate(-4deg) translateY(4px);
  transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.tilt-card:hover { transform: rotate(0deg) translateY(0px); }
```

Hover rules:
```css
.task-card:hover         { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }
.participant-card:hover  { transform: scale(1.05); }
.reminder-card:hover     { transform: scale(1.02); }
```

---

## 8. The Quality Bar Checklist

Before shipping, verify:

- [ ] Outer shell uses `rounded-3xl` and `shadow-xl`/`shadow-2xl`
- [ ] One single `--color-primary` is used consistently
- [ ] Hang-up button is **red** and **larger** than other toolbar buttons
- [ ] All toolbar buttons are circular with `backdrop-blur-sm bg-white/20`
- [ ] Recording badge has `animate-pulse` red dot
- [ ] All `<img>` use `object-cover` and come from `people-library` (NOT pravatar / unsplash)
- [ ] Plus Jakarta Sans is the UI font; weight hierarchy bold→semibold→medium
- [ ] Status dots: green=on, red=muted, yellow=raised hand
- [ ] Page ends with `<script>if (window.lucide) lucide.createIcons();</script>`
- [ ] No emoji-only icons; all functional icons use Lucide
- [ ] No outdated stock URLs (i.pravatar.cc, unsplash.com, hellorf.com, etc.)
- [ ] If grid: gap is `gap-3` to `gap-5`; tiles `rounded-2xl`
- [ ] If chat: messages use asymmetric `rounded-tl-sm` / `rounded-tr-sm` corner
- [ ] Hover states defined on every interactive element

If all 14 pass, output matches the quality bar of the 12 reference templates.
