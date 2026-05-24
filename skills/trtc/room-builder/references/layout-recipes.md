# Room UI Layout Recipes

The 12 reference templates collapse into **6 reusable layout skeletons**. When asked to "design a meeting screen for X", first decide which skeleton fits, then plug in components from `component-library.md`.

---

## Skeleton 1 — "Dashboard Shell" (Sidebar + Video + Right Panel)

**Used by:** templates 01, 02, 12 — most common layout.

```
┌─[shell rounded-3xl]──────────────────────────────────┐
│ ┌NAV┐ ┌────────────────────────┐ ┌──────────────┐   │
│ │ 72│ │ TopBar                 │ │ Right Panel  │   │
│ │ px│ ├────────────────────────┤ │ (Chat /      │   │
│ │   │ │   VIDEO STAGE          │ │  Participants│   │
│ │   │ │   (380px or flex-1)    │ │  / Notes)    │   │
│ │   │ ├────────────────────────┤ │              │   │
│ │   │ │ (optional bottom row)  │ │              │   │
│ └───┘ └────────────────────────┘ └──────────────┘   │
└──────────────────────────────────────────────────────┘
```

```html
<div class="w-full max-w-[1400px] h-[840px] bg-card rounded-3xl shadow-2xl overflow-hidden flex">
  <!-- B1: NavRail -->
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- B2/B3: TopHeader -->
    <!-- C1: VideoStage -->
  </div>
  <!-- F1 or E2: Right panel -->
</div>
```

**When to use:** Default for product demos, single-active-speaker calls, customer support.

---

## Skeleton 2 — "Tri-column Card" (Free-flow, no shell)

**Used by:** templates 04, 05.

```
┌─VIDEO COLUMN────────────┐ ┌─CHAT COLUMN─┐ ┌AVATAR┐
│ [TopBar card]           │ │ Participants│ │ COLUMN│
│ [Video card 16:9]       │ │ Chat        │ │ (vert)│
│ [Thumbnail strip card]  │ │             │ │       │
│ [Toolbar (centered)]    │ │             │ │       │
└─────────────────────────┘ └─────────────┘ └──────┘
```

```html
<div class="w-[1380px] flex gap-5 mx-auto">
  <div class="flex-1 flex flex-col gap-4">
    <div class="bg-card rounded-2xl px-5 py-3 shadow-sm">...</div>
    <div class="rounded-3xl overflow-hidden aspect-[16/9] shadow-xl">...</div>
    <div class="bg-card rounded-2xl p-3 flex gap-3">...</div>
    <div class="flex justify-center gap-3 py-2">...</div>
  </div>
  <div class="w-[320px] flex flex-col gap-4">...</div>
  <div class="w-12 flex flex-col items-center gap-3 pt-16">...</div>
</div>
```

**When to use:** Sprint planning, casual standups, when each section needs breathing room.

---

## Skeleton 3 — "Equal Grid" (2×2 or 3×3)

**Used by:** templates 07 (2×2), 09 (3×3).

```
┌─Top fixed bar──────────────────────────────┐
│ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│ │  Tile 1  │ │  Tile 2  │ │  Tile 3  │   │
│ ├──────────┤ ├──────────┤ ├──────────┤   │
│ │  Tile 4  │ │  Tile 5  │ │  Tile 6  │   │
│ └──────────┘ └──────────┘ └──────────┘   │
│              [Floating Toolbar]            │
└────────────────────────────────────────────┘
```

```html
<body class="bg-... min-h-screen overflow-hidden">
  <div class="fixed top-0 left-0 right-0 z-50 h-14 ..."> ... </div>
  <div class="pt-14 h-screen p-5 grid grid-cols-2 grid-rows-2 gap-5">
    <!-- Repeat C4 tile × 4 (or × 9 with grid-cols-3 grid-rows-3) -->
  </div>
  <div class="fixed bottom-5 left-1/2 -translate-x-1/2 z-50">...</div>
</body>
```

**When to use:** Symmetric calls (no presenter), team standups, all-hands, classroom mode.

---

## Skeleton 4 — "1-up + Thumb Strip"

**Used by:** templates 08, 11.

```
┌─Top fixed bar──────────────────────────────┐
│ ┌────────────────────────┐ ┌─Right Panel─┐ │
│ │   MAIN SPEAKER         │ │ Participants│ │
│ │   (flex-1)             │ │ List        │ │
│ ├────────────────────────┤ │             │ │
│ │ [thumb][thumb][thumb]  │ │             │ │
│ └────────────────────────┘ └─────────────┘ │
│              [Floating Toolbar]            │
└────────────────────────────────────────────┘
```

```html
<div class="pt-14 flex h-screen">
  <div class="w-64 border-r p-4">...</div>  <!-- optional agenda for #11 -->
  <div class="flex-1 p-5 flex flex-col gap-4">
    <div class="flex-1 relative rounded-2xl overflow-hidden">...</div>
    <div class="flex gap-3 h-28 sm:h-36"> <!-- 4–5 tiles --> </div>
  </div>
  <div class="w-72 border-l">...</div>
</div>
```

**When to use:** Premium / formal meetings (executive boards, workshops). Main speaker dominant.

---

## Skeleton 5 — "AI-Augmented" (Video + Live Notes)

**Used by:** templates 03, 06.

```
┌─[shell]──────────────────────────────────────────┐
│ ┌NAV┐ ┌──────────────────────┐ ┌──────────────┐ │
│ │   │ │ Header               │ │ Records      │ │
│ │   │ ├──────────────────────┤ │ (gradient)   │ │
│ │   │ │  VIDEO STAGE         │ ├──────────────┤ │
│ │   │ ├──────────────────────┤ │ Upcoming     │ │
│ │   │ │ ┌AI Notes┐ ┌Members┐ │ │              │ │
│ │   │ │ │  • ... │ │ list  │ │ │              │ │
│ │   │ │ └────────┘ └───────┘ │ │              │ │
│ └───┘ └──────────────────────┘ └──────────────┘ │
└──────────────────────────────────────────────────┘
```

Bottom row of main column splits into TWO equal cards (AI notes + team list).

**When to use:** AI-powered meeting products, project onboarding, smart-recap features.

---

## Skeleton 6 — "Glass Floating" (Light, immersive)

**Used by:** templates 09, 10.

```
┌─Decorative bg (gradient + radial blobs)─────┐
│ ┌─Title bar (glass)──┐                      │
│ │  VIDEO (glass card) │   ┌─Right Tabs────┐ │
│ │                     │   │  Chat / Notes │ │
│ │ Left thumb column   │   │  / Files      │ │
│ │ (vertical, w-24)    │   └───────────────┘ │
│         [Glass floating toolbar]             │
└──────────────────────────────────────────────┘
```

Glass utilities (always include):
```css
.glass {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.35);
}
.glass-strong {
  background: rgba(255, 255, 255, 0.45);
  backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.5);
}
```

**When to use:** Premium consumer products, brand-design reviews, "soft" / aspirational feel.

---

## Skeleton Selection Decision Tree

```
What is the meeting style?

├── One dominant speaker + side context?
│   ├── Polished SaaS shell?           → Skeleton 1 (Dashboard)
│   ├── Each block to "breathe"?       → Skeleton 2 (Tri-column Card)
│   ├── Premium / formal mood?         → Skeleton 4 (1-up + Thumb)
│   └── AI features prominent?         → Skeleton 5 (AI-Augmented)
│
├── Equal participants (no presenter)?
│   ├── 4 people                       → Skeleton 3 with 2×2 grid
│   └── 6–9+ people                    → Skeleton 3 with 3×3 grid
│
└── Premium consumer / aspirational?   → Skeleton 6 (Glass Floating)
```

---

## Density Rules

| Participant count | Recommended skeleton | Tile size |
|---|---|---|
| 1–2 | Skeleton 1, 2, or 5 | Hero only, no thumbs |
| 3–5 | Skeleton 1, 2, or 4 | Hero + thumb strip |
| 6–8 | Skeleton 4 or 3 (2×2 + overflow) | Equal medium tiles |
| 9–12 | Skeleton 3 (3×3 + chat bubble) | Smaller equal tiles |
| 12+ | Skeleton 3 (3×3) + "+N more" overflow chip | Tiny tiles + counter |

---

## Common Modifiers

Sprinkle on top of any skeleton:

- **Recording state** → D5 to top-right of video.
- **Live captions** → G1 below video, OR G2 overlay at bottom of video tile.
- **Raised hand** → yellow status dot or top-right pill `<i data-lucide="hand">`.
- **Active speaker glow** → `style="animation: speakerGlow 2.5s ease-in-out infinite;"` on speaking tile.
- **Encrypted indicator** → `<i data-lucide="shield-check">` + label in top bar.
- **Join request** → H6 pill in top bar.
- **Meeting code** → `<div class="bg-gray-100 rounded-full px-3 py-1.5"><span class="text-xs font-mono">jhp-cmiw-jic</span><i data-lucide="copy" class="w-3 h-3"></i></div>` top-right.
