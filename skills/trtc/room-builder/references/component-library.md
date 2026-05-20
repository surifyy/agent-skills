# Room UI Component Library — Copy-Paste Snippets

Production-ready HTML snippets that conform to `design-system.md`. Each is self-contained (apart from page-level Tailwind/Lucide setup) and can be combined to assemble a Room UI.

> Convention: portraits at `../../people-library/assets/portraits/<id>.png`. Replace with project-relative paths when shipping.

## Sections
- A. Page Skeleton
- B. Navigation & Headers
- C. Video Stage
- D. Toolbars
- E. Participants
- F. Chat
- G. AI / Captions / Summary
- H. Side Cards

---

## A. Page Skeleton

### A1 — Standard 3-column shell

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Meeting</title>
  <link rel="preconnect" href="https://unpkg.com" />
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
  <script src="https://unpkg.com/@fortawesome/fontawesome-free@6.7.2/js/all.min.js"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>* { scrollbar-width: none; }</style>
</head>
<body class="bg-neutral-50 min-h-screen flex items-center justify-center p-6">
<link href="https://fonts.googleapis.cn/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style type="text/tailwindcss">
@theme {
  --color-primary: #4F6EF7;
  --color-primary-dark: #3B58E0;
  --color-primary-light: #EEF1FE;
  --color-card: #FFFFFF;
  --color-sidebar-bg: #FAFBFC;
  --font-main: 'Plus Jakarta Sans', sans-serif;
  --font-body: 'DM Sans', sans-serif;
}
body { font-family: var(--font-body); }
</style>

<div class="w-full max-w-[1400px] h-[840px] bg-card rounded-3xl shadow-2xl overflow-hidden flex">
  <!-- LEFT NAV RAIL (B1) -->
  <div class="flex-1 flex flex-col">
    <!-- TOP HEADER (B2/B3) + VIDEO STAGE (C1) -->
  </div>
  <!-- RIGHT PANEL (F1 / E2 / G1) -->
</div>

<script>if (window.lucide) lucide.createIcons();</script>
</body>
</html>
```

### A2 — Full-screen immersive shell (for grids)

```html
<body class="bg-[#0A0A0F] text-white min-h-screen overflow-hidden">
  <div class="fixed top-0 left-0 right-0 z-50 h-14 flex items-center justify-between px-8 bg-[#0A0A0F]/80 backdrop-blur-2xl border-b border-white/10"> ... </div>
  <div class="pt-14 h-screen p-5 grid grid-cols-2 grid-rows-2 gap-5"> ... </div>
  <div class="fixed bottom-5 left-1/2 -translate-x-1/2 z-50"> ... </div>
</body>
```

---

## B. Navigation & Headers

### B1 — Left Nav Rail

```html
<div class="w-[72px] bg-sidebar-bg border-r border-neutral-100 flex flex-col items-center py-5 gap-2">
  <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-400 to-blue-500 flex items-center justify-center mb-4 shadow-lg shadow-sky-300/30">
    <i data-lucide="zap" class="w-5 h-5 text-white"></i>
  </div>
  <button class="w-10 h-10 rounded-xl flex items-center justify-center bg-primary text-white">
    <i data-lucide="layout-dashboard" class="w-5 h-5"></i>
  </button>
  <button class="w-10 h-10 rounded-xl flex items-center justify-center text-neutral-400 hover:bg-primary/10 transition-colors">
    <i data-lucide="message-circle" class="w-5 h-5"></i>
  </button>
  <button class="w-10 h-10 rounded-xl flex items-center justify-center text-neutral-400 hover:bg-primary/10 transition-colors">
    <i data-lucide="calendar" class="w-5 h-5"></i>
  </button>
  <button class="w-10 h-10 rounded-xl flex items-center justify-center text-neutral-400 hover:bg-primary/10 transition-colors">
    <i data-lucide="settings" class="w-5 h-5"></i>
  </button>
  <div class="mt-auto">
    <img src="../../people-library/assets/portraits/m01-casual-friendly-man-airpods.png"
         class="w-10 h-10 rounded-full object-cover border-2 border-primary/30" />
  </div>
</div>
```

### B2 — Top Header (title + back + actions)

```html
<div class="px-6 py-4 flex items-center justify-between border-b border-neutral-100">
  <div class="flex items-center gap-4">
    <button class="w-9 h-9 rounded-full hover:bg-neutral-100 flex items-center justify-center transition-colors">
      <i data-lucide="arrow-left" class="w-5 h-5 text-neutral-500"></i>
    </button>
    <div>
      <h1 class="text-lg font-bold text-neutral-800" style="font-family:var(--font-main)">Page Title</h1>
      <p class="text-xs text-neutral-400 mt-0.5">Subtitle · 6 participants</p>
    </div>
  </div>
  <div class="flex items-center gap-3">
    <span class="bg-primary-light text-primary text-xs font-semibold px-3 py-1.5 rounded-full">Team</span>
    <button class="bg-primary text-white text-sm font-semibold px-4 py-2 rounded-xl hover:opacity-90 transition-opacity flex items-center gap-1.5">
      <i data-lucide="user-plus" class="w-4 h-4"></i>
      Add user
    </button>
  </div>
</div>
```

### B3 — Search + Bell + User chip

```html
<div class="px-6 py-4 flex items-center justify-between">
  <div class="flex-1 max-w-md flex items-center gap-2 bg-neutral-50 rounded-xl px-4 py-2.5 border border-neutral-100">
    <i data-lucide="search" class="w-4 h-4 text-neutral-400"></i>
    <input type="text" placeholder="Search here..." class="flex-1 text-sm bg-transparent outline-none placeholder:text-neutral-400" />
  </div>
  <div class="flex items-center gap-4">
    <button class="relative w-10 h-10 rounded-xl hover:bg-neutral-100 flex items-center justify-center transition-colors">
      <i data-lucide="bell" class="w-5 h-5 text-neutral-500"></i>
      <div class="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full"></div>
    </button>
    <div class="flex items-center gap-2">
      <span class="text-sm font-semibold text-neutral-700">Mrinmoy K</span>
      <img src="../../people-library/assets/portraits/m01-casual-friendly-man-airpods.png" class="w-9 h-9 rounded-full object-cover" />
    </div>
  </div>
</div>
```

---

## C. Video Stage

### C1 — Hero speaker tile (full kit)

```html
<div class="relative rounded-2xl overflow-hidden bg-neutral-800 h-[380px]">
  <img src="../../people-library/assets/portraits/m04-business-man-blue-shirt.png"
       class="w-full h-full object-cover" />
  <div class="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent"></div>

  <!-- Top-left: stacked attendee avatars -->
  <div class="absolute top-4 left-4 flex -space-x-2">
    <img src="../../people-library/assets/portraits/f01-senior-pro-woman-navy-blouse.png" class="w-9 h-9 rounded-full object-cover border-2 border-white shadow-md" />
    <img src="../../people-library/assets/portraits/m02-focused-black-man-headphones.png" class="w-9 h-9 rounded-full object-cover border-2 border-white shadow-md" />
    <img src="../../people-library/assets/portraits/f03-friendly-woman-plaid-blazer.png" class="w-9 h-9 rounded-full object-cover border-2 border-white shadow-md" />
  </div>

  <!-- Top-right: REC pill -->
  <div class="absolute top-4 right-4 bg-black/60 backdrop-blur-sm rounded-full px-3 py-1.5 flex items-center gap-2">
    <div class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
    <span class="text-white text-xs font-mono font-medium">00:15:16</span>
  </div>

  <!-- Left: vertical volume slider -->
  <div class="absolute left-4 top-1/2 -translate-y-1/2">
    <div class="w-1.5 h-28 bg-white/20 rounded-full relative">
      <div class="absolute bottom-0 w-full h-[55%] bg-primary rounded-full"></div>
      <div class="absolute bottom-[55%] left-1/2 -translate-x-1/2 w-3.5 h-3.5 bg-white rounded-full shadow -translate-y-1/2"></div>
    </div>
  </div>

  <!-- Bottom-center: D1 toolbar -->
</div>
```

### C2 — Speaker info card (top-left)

```html
<div class="absolute top-4 left-4 bg-black/40 backdrop-blur-sm rounded-xl px-3 py-2 flex items-center gap-2.5">
  <img src="../../people-library/assets/portraits/f01-senior-pro-woman-navy-blouse.png"
       class="w-7 h-7 rounded-full object-cover border border-white/50" />
  <div>
    <p class="text-[10px] text-white/60 font-medium">Publisher</p>
    <p class="text-xs text-white font-semibold">Kate Smith</p>
  </div>
</div>
```

### C3 — Picture-in-picture inset

```html
<div class="absolute top-4 right-4 w-36 h-24 rounded-xl overflow-hidden border-[3px] border-yellow-300 shadow-lg">
  <img src="../../people-library/assets/portraits/m04-business-man-blue-shirt.png" class="w-full h-full object-cover" />
</div>
```

### C4 — 2×2 video grid tile

```html
<div class="relative rounded-2xl overflow-hidden bg-neutral-800 group">
  <img src="../../people-library/assets/portraits/f01-senior-pro-woman-navy-blouse.png" class="w-full h-full object-cover" />
  <div class="absolute inset-0 bg-gradient-to-t from-black/55 via-transparent to-black/10"></div>
  <div class="absolute top-4 left-4 px-3 py-1 rounded-lg bg-primary/90 text-white text-[10px] font-bold">Host</div>
  <div class="absolute bottom-4 left-4 flex items-center gap-2">
    <span class="text-white text-xs font-medium drop-shadow">Eva Morrison</span>
    <i data-lucide="mic" class="w-3.5 h-3.5 text-white/90"></i>
  </div>
  <div class="absolute bottom-4 right-4 flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
    <button class="w-7 h-7 rounded-lg bg-white/20 backdrop-blur flex items-center justify-center"><i data-lucide="pin" class="w-3 h-3 text-white"></i></button>
    <button class="w-7 h-7 rounded-lg bg-white/20 backdrop-blur flex items-center justify-center"><i data-lucide="maximize-2" class="w-3 h-3 text-white"></i></button>
  </div>
</div>
```

### C5 — Thumbnail strip

```html
<div class="flex gap-3">
  <div class="relative w-[120px] h-[80px] rounded-xl overflow-hidden bg-gray-200 flex-shrink-0">
    <img src="../../people-library/assets/portraits/f01-senior-pro-woman-navy-blouse.png" class="w-full h-full object-cover" />
    <div class="absolute bottom-1 left-1 right-1 text-center text-[9px] text-white font-medium bg-black/40 rounded-md py-0.5 truncate">Name</div>
  </div>
</div>
```

### C6 — Vertical thumbnail column (right side)

```html
<div class="w-[70px] flex flex-col gap-3 flex-shrink-0">
  <div class="relative bg-white rounded-xl shadow-sm border border-neutral-100 p-1.5 hover:scale-105 transition-transform cursor-pointer">
    <img src="../../people-library/assets/portraits/f03-friendly-woman-plaid-blazer.png" class="w-full aspect-square rounded-lg object-cover" />
    <div class="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white"></div>
  </div>
</div>
```

---

## D. Toolbars

### D1 — In-video bottom toolbar (overlay)

```html
<div class="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-3">
  <button class="w-11 h-11 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors">
    <i data-lucide="video" class="w-4 h-4 text-white"></i>
  </button>
  <button class="w-11 h-11 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors">
    <i data-lucide="mic" class="w-4 h-4 text-white"></i>
  </button>
  <button class="w-11 h-11 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors">
    <i data-lucide="users" class="w-4 h-4 text-white"></i>
  </button>
  <button class="w-12 h-12 rounded-full bg-red-500 flex items-center justify-center hover:bg-red-600 transition-colors shadow-lg shadow-red-500/30">
    <i data-lucide="phone-off" class="w-5 h-5 text-white"></i>
  </button>
  <button class="w-11 h-11 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors">
    <i data-lucide="monitor-up" class="w-4 h-4 text-white"></i>
  </button>
  <button class="w-11 h-11 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-colors">
    <i data-lucide="settings" class="w-4 h-4 text-white"></i>
  </button>
</div>
```

### D2 — Floating bottom toolbar (full-screen)

```html
<div class="fixed bottom-5 left-1/2 -translate-x-1/2 z-50">
  <div class="flex items-center gap-2 px-7 py-3 rounded-2xl bg-primary shadow-xl shadow-primary/30">
    <button class="w-11 h-11 rounded-[14px] bg-white/10 hover:bg-white/20 flex items-center justify-center transition-all">
      <i data-lucide="mic" class="w-5 h-5 text-white/90"></i>
    </button>
    <button class="w-11 h-11 rounded-[14px] bg-white/10 hover:bg-white/20 flex items-center justify-center transition-all">
      <i data-lucide="video" class="w-5 h-5 text-white/90"></i>
    </button>
    <button class="w-11 h-11 rounded-[14px] bg-white/20 hover:bg-white/30 flex items-center justify-center transition-all border border-white/30">
      <i data-lucide="monitor-up" class="w-5 h-5 text-white"></i>
    </button>
    <div class="w-px h-6 bg-white/10 mx-1"></div>
    <button class="w-11 h-11 rounded-[14px] bg-white/10 hover:bg-white/20 flex items-center justify-center transition-all">
      <i data-lucide="hand" class="w-5 h-5 text-white/90"></i>
    </button>
    <button class="w-11 h-11 rounded-[14px] bg-white/10 hover:bg-white/20 flex items-center justify-center transition-all">
      <i data-lucide="message-square" class="w-5 h-5 text-white/90"></i>
    </button>
    <div class="w-px h-6 bg-white/10 mx-1"></div>
    <button class="h-11 px-5 rounded-[14px] bg-red-500/90 hover:bg-red-500 transition-all flex items-center gap-2">
      <i data-lucide="phone-off" class="w-4 h-4 text-white"></i>
      <span class="text-xs font-bold text-white">Leave</span>
    </button>
  </div>
</div>
```

### D3 — Detached white-card toolbar (sits below video)

```html
<div class="flex items-center justify-center gap-3 py-2">
  <button class="w-11 h-11 rounded-full bg-primary flex items-center justify-center hover:bg-primary-dark transition-colors shadow-md">
    <i data-lucide="video" class="w-5 h-5 text-white"></i>
  </button>
  <button class="w-11 h-11 rounded-full bg-orange-500 flex items-center justify-center hover:bg-orange-600 transition-colors shadow-md">
    <i data-lucide="mic-off" class="w-5 h-5 text-white"></i>
  </button>
  <button class="w-11 h-11 rounded-full bg-white flex items-center justify-center hover:bg-gray-50 transition-colors shadow-md">
    <i data-lucide="hand" class="w-5 h-5 text-gray-600"></i>
  </button>
  <button class="w-11 h-11 rounded-full bg-red-500 flex items-center justify-center hover:bg-red-600 transition-colors shadow-md">
    <i data-lucide="phone-off" class="w-5 h-5 text-white"></i>
  </button>
</div>
```

### D4 — Glassmorphism toolbar (light)

```html
<div class="fixed bottom-5 left-1/2 -translate-x-1/2 z-50">
  <div class="flex items-center gap-2.5 px-6 py-3 rounded-3xl shadow-2xl"
       style="background: rgba(255,255,255,0.45); backdrop-filter: blur(30px); border: 1px solid rgba(255,255,255,0.5);">
    <button class="w-11 h-11 rounded-2xl bg-white/40 hover:bg-white/60 flex items-center justify-center transition-all shadow-sm">
      <i data-lucide="mic" class="w-5 h-5 text-neutral-800"></i>
    </button>
  </div>
</div>
```

### D5 — Recording badge

```html
<!-- Variant A: dark glass + monospace timer -->
<div class="absolute top-4 right-4 bg-black/60 backdrop-blur-sm rounded-full px-3 py-1.5 flex items-center gap-2">
  <div class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
  <span class="text-white text-xs font-mono font-medium">00:15:16</span>
</div>

<!-- Variant B: minimal REC -->
<div class="px-3 py-1 rounded-full bg-red-500/10 text-red-400 text-[11px] font-medium flex items-center gap-1.5">
  <span class="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span> REC
</div>
```

---

## E. Participants

### E1 — Avatar group + count chip

```html
<div class="flex items-center">
  <img src="../../people-library/assets/portraits/m01-casual-friendly-man-airpods.png" class="w-8 h-8 rounded-full object-cover border-2 border-white" />
  <img src="../../people-library/assets/portraits/f01-senior-pro-woman-navy-blouse.png" class="w-8 h-8 rounded-full object-cover border-2 border-white -ml-2.5" />
  <img src="../../people-library/assets/portraits/m02-focused-black-man-headphones.png" class="w-8 h-8 rounded-full object-cover border-2 border-white -ml-2.5" />
  <span class="w-8 h-8 rounded-full bg-primary-light text-primary text-xs font-semibold flex items-center justify-center -ml-2.5 border-2 border-white">+32</span>
</div>
```

### E2 — Participants list panel

```html
<div class="w-72 border-l border-neutral-100 bg-white/60 backdrop-blur-xl flex flex-col">
  <div class="p-4 border-b border-neutral-100 flex items-center justify-between">
    <div class="flex items-center gap-2">
      <i data-lucide="users" class="w-4 h-4 text-primary"></i>
      <span class="text-sm font-semibold">Participants</span>
      <span class="text-[10px] text-neutral-400 bg-neutral-100 px-2 py-0.5 rounded-full">8</span>
    </div>
  </div>
  <div class="flex-1 overflow-y-auto p-3 space-y-1">
    <div class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-neutral-50 transition-colors group">
      <div class="relative">
        <img src="../../people-library/assets/portraits/m06-ceo-silverhair-suit.png" class="w-8 h-8 rounded-full object-cover" />
        <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-green-500 rounded-full border-2 border-white"></span>
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-xs font-medium truncate">Sarah Reynolds</p>
        <p class="text-[10px] text-primary">Host · Presenting</p>
      </div>
      <i data-lucide="mic" class="w-3.5 h-3.5 text-primary opacity-0 group-hover:opacity-100 transition-opacity"></i>
    </div>
  </div>
</div>
```

### E3 — Status dot variants

```html
<!-- Online green -->
<div class="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-green-500 rounded-full border-2 border-white"></div>
<!-- Muted red w/ icon -->
<div class="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-red-500 rounded-full border-2 border-white flex items-center justify-center">
  <i data-lucide="mic-off" class="w-2.5 h-2.5 text-white"></i>
</div>
<!-- Raised hand yellow -->
<div class="absolute -bottom-0.5 -right-0.5 w-4 h-4 bg-yellow-500 rounded-full border-2 border-white"></div>
```

### E4 — Status pill

```html
<span class="text-[10px] font-semibold px-2.5 py-1 rounded-full bg-primary/10 text-primary">On Meeting</span>
<span class="text-[10px] font-semibold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-600">Active</span>
<span class="text-[10px] font-semibold px-2.5 py-1 rounded-full bg-gray-100 text-gray-400">Inactive</span>
<span class="text-[10px] font-semibold px-2.5 py-1 rounded-full bg-red-50 text-red-500">Absent</span>
```

---

## F. Chat

### F1 — Right-side chat panel (full)

```html
<div class="w-[340px] border-l border-neutral-100 flex flex-col bg-white">
  <div class="px-5 pt-5 pb-3">
    <h2 class="text-lg font-bold text-neutral-800 mb-4" style="font-family:var(--font-main)">Live Chat</h2>
    <div class="flex gap-6 border-b border-neutral-100">
      <button class="pb-2.5 text-sm font-semibold text-primary border-b-2 border-primary">Messages</button>
      <button class="pb-2.5 text-sm font-medium text-neutral-400 hover:text-neutral-600 transition-colors">Participants</button>
    </div>
  </div>
  <div class="flex-1 overflow-y-auto px-5 py-3 space-y-4">
    <!-- F2 / F3 message bubbles -->
  </div>
  <div class="px-4 pb-4">
    <div class="flex items-center gap-2 bg-neutral-50 rounded-2xl px-4 py-3 border border-neutral-100">
      <button class="hover:bg-neutral-200 rounded-full p-1 transition-colors">
        <i data-lucide="smile" class="w-4 h-4 text-neutral-400"></i>
      </button>
      <input type="text" placeholder="Write your message..." class="flex-1 text-sm text-neutral-600 outline-none bg-transparent placeholder:text-neutral-400" />
      <button class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center hover:opacity-90 transition-opacity">
        <i data-lucide="send" class="w-4 h-4 text-white"></i>
      </button>
    </div>
  </div>
</div>
```

### F2 — Message bubble (other, left)

```html
<div class="flex items-start gap-2.5">
  <img src="../../people-library/assets/portraits/m02-focused-black-man-headphones.png" class="w-8 h-8 rounded-full object-cover flex-shrink-0" />
  <div>
    <div class="flex items-baseline gap-2 mb-1">
      <span class="text-xs font-semibold text-neutral-800">John Hudson</span>
      <span class="text-[10px] text-neutral-400">9:31 AM</span>
    </div>
    <div class="bg-neutral-100 rounded-2xl rounded-tl-sm px-3.5 py-2.5">
      <p class="text-sm text-neutral-700">Yes! I've prepared the market analysis</p>
    </div>
  </div>
</div>
```

### F3 — Message bubble (self, right, primary)

```html
<div class="flex items-start gap-2.5 flex-row-reverse">
  <img src="../../people-library/assets/portraits/m01-casual-friendly-man-airpods.png" class="w-8 h-8 rounded-full object-cover flex-shrink-0" />
  <div class="text-right">
    <div class="flex items-baseline gap-2 mb-1 justify-end">
      <span class="text-[10px] text-neutral-400">9:32 AM</span>
      <span class="text-xs font-semibold text-neutral-800">You</span>
    </div>
    <div class="bg-primary rounded-2xl rounded-tr-sm px-3.5 py-2.5">
      <p class="text-sm text-white">Great, let's start with the downtown location</p>
    </div>
  </div>
</div>
```

### F4 — System message

```html
<div class="text-center">
  <span class="text-[10px] text-neutral-400 bg-neutral-50 px-3 py-1 rounded-full">Kate Smith started the call</span>
</div>
```

### F5 — Typing indicator

```html
<div class="flex items-center gap-2 px-1">
  <div class="flex gap-1">
    <div class="w-1.5 h-1.5 bg-primary/50 rounded-full animate-bounce" style="animation-delay:0s"></div>
    <div class="w-1.5 h-1.5 bg-primary/50 rounded-full animate-bounce" style="animation-delay:0.15s"></div>
    <div class="w-1.5 h-1.5 bg-primary/50 rounded-full animate-bounce" style="animation-delay:0.3s"></div>
  </div>
  <span class="text-xs text-neutral-400 italic">Martin is typing</span>
</div>
```

### F6 — Floating chat bubble (dark mode)

```html
<div class="fixed bottom-24 right-5 z-50 w-72">
  <div class="rounded-2xl bg-white/5 backdrop-blur-2xl border border-white/10 overflow-hidden">
    <div class="p-3 border-b border-white/5 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <i data-lucide="message-circle" class="w-3.5 h-3.5 text-primary"></i>
        <span class="text-[11px] font-semibold text-white">Chat</span>
        <span class="w-4 h-4 rounded-full bg-primary/20 text-primary text-[9px] flex items-center justify-center font-bold">3</span>
      </div>
      <i data-lucide="chevron-down" class="w-3.5 h-3.5 text-white/40"></i>
    </div>
    <div class="p-3 space-y-2.5 max-h-40 overflow-y-auto"></div>
  </div>
</div>
```

---

## G. AI / Captions / Summary

### G1 — Live caption bar (below video)

```html
<div class="rounded-xl px-4 py-3 flex items-center gap-3 border border-primary/10"
     style="background: linear-gradient(90deg, rgba(45,106,79,0.08) 0%, transparent 100%);">
  <span class="text-xs font-semibold text-primary bg-primary/10 px-2 py-0.5 rounded">Now</span>
  <div class="flex items-center gap-0.5 h-4">
    <div class="w-1 h-2 bg-primary/60 rounded-full"></div>
    <div class="w-1 h-3.5 bg-primary/80 rounded-full"></div>
    <div class="w-1 h-4 bg-primary rounded-full"></div>
    <div class="w-1 h-3 bg-primary/80 rounded-full"></div>
    <div class="w-1 h-2 bg-primary/50 rounded-full"></div>
  </div>
  <p class="text-sm text-neutral-500 flex-1">Live caption text appears here...</p>
</div>
```

### G2 — Auto-translator overlay

```html
<div class="absolute bottom-0 inset-x-0 bg-gray-900/80 backdrop-blur-sm px-4 py-3 flex items-center gap-3">
  <span class="text-[10px] font-semibold text-gray-400 bg-gray-700 px-2 py-0.5 rounded-full flex-shrink-0">Auto Translator</span>
  <p class="text-xs text-white/90 leading-relaxed">Hi everyone, today we'll discuss...</p>
</div>
```

### G3 — Audio waveform (long)

```html
<div class="flex items-center gap-0.5 h-8 mb-3">
  <div class="w-1 bg-primary/30 rounded-full h-3"></div>
  <div class="w-1 bg-primary/50 rounded-full h-5"></div>
  <div class="w-1 bg-primary/70 rounded-full h-7"></div>
  <div class="w-1 bg-primary    rounded-full h-8"></div>
  <div class="w-1 bg-primary/70 rounded-full h-6"></div>
  <div class="w-1 bg-primary/50 rounded-full h-4"></div>
  <div class="w-1 bg-primary/60 rounded-full h-7"></div>
  <div class="w-1 bg-primary    rounded-full h-8"></div>
  <div class="w-1 bg-primary/40 rounded-full h-4"></div>
</div>
```

### G4 — Live summary timeline

```html
<div class="bg-neutral-50 rounded-2xl border border-neutral-100 p-4">
  <div class="flex items-center justify-between mb-3">
    <h3 class="text-sm font-bold text-neutral-900">Live summary</h3>
    <div class="flex gap-0.5">
      <div class="w-1 h-1 rounded-full bg-neutral-300 animate-bounce" style="animation-delay:0s"></div>
      <div class="w-1 h-1 rounded-full bg-neutral-300 animate-bounce" style="animation-delay:0.15s"></div>
      <div class="w-1 h-1 rounded-full bg-neutral-300 animate-bounce" style="animation-delay:0.3s"></div>
    </div>
  </div>
  <div class="space-y-1.5">
    <div class="flex items-start gap-2">
      <div class="w-1 min-h-[32px] rounded-full bg-neutral-900 flex-shrink-0 mt-0.5"></div>
      <div>
        <span class="text-[10px] text-neutral-400">17:20</span>
        <p class="text-[11px] font-bold text-neutral-900">Visual Design Direction</p>
      </div>
    </div>
    <div class="flex items-start gap-2">
      <div class="w-1 min-h-[32px] rounded-full bg-neutral-200 flex-shrink-0 mt-0.5"></div>
      <div>
        <span class="text-[10px] text-neutral-400">16:56</span>
        <p class="text-[11px] text-neutral-500">Game Mechanics Discussion</p>
      </div>
    </div>
  </div>
</div>
```

---

## H. Side Cards

### H1 — Reminder / upcoming meeting card

```html
<div class="rounded-2xl p-4 transition-transform hover:-translate-y-0.5"
     style="background: linear-gradient(135deg, #7C5CFC, #9B82FC);">
  <div class="flex items-start justify-between mb-3">
    <div>
      <h4 class="text-white font-semibold text-sm">Nexus Project</h4>
      <p class="text-white/60 text-xs mt-0.5">3 Participants</p>
    </div>
    <span class="w-3 h-3 rounded-full bg-white mt-1"></span>
  </div>
  <div class="flex items-center gap-1.5 text-white/70 text-xs">
    <i data-lucide="clock" class="w-3.5 h-3.5"></i>
    <span>9:00 am</span>
  </div>
</div>
```

### H2 — Stacked reminder cards

```html
<div class="relative h-[130px]">
  <div class="absolute top-3 left-2 right-2 bg-gradient-to-r from-emerald-500 to-green-400 rounded-2xl p-4 shadow-lg">
    <p class="text-white text-sm font-semibold">Design Meeting with Hulu</p>
    <p class="text-white/70 text-xs">05:30 PM</p>
  </div>
  <div class="absolute top-0 left-0 right-0 bg-white rounded-2xl p-4 shadow-xl border border-neutral-100 z-10">
    <p class="text-neutral-800 text-sm font-bold">Meeting with Google team</p>
    <p class="text-primary text-xs font-semibold">12:30 AM</p>
  </div>
</div>
```

### H3 — Task card with checkboxes

```html
<div class="bg-white rounded-2xl p-4 border border-neutral-100 hover:-translate-y-0.5 hover:shadow-lg transition-all cursor-pointer">
  <div class="flex items-center gap-2 mb-3">
    <div class="w-8 h-8 rounded-lg bg-amber-100 flex items-center justify-center">
      <i data-lucide="palette" class="w-4 h-4 text-amber-600"></i>
    </div>
    <span class="text-sm font-bold text-neutral-800">Brand System</span>
  </div>
  <div class="space-y-2 mb-3">
    <div class="flex items-center gap-2">
      <div class="w-4 h-4 rounded border-2 border-primary bg-primary/10 flex items-center justify-center">
        <i data-lucide="check" class="w-2.5 h-2.5 text-primary"></i>
      </div>
      <span class="text-xs text-neutral-600">Moodboard Creation</span>
    </div>
    <div class="flex items-center gap-2">
      <div class="w-4 h-4 rounded border-2 border-neutral-200"></div>
      <span class="text-xs text-neutral-500">Color Palette Draft</span>
    </div>
  </div>
  <div class="flex items-center justify-between">
    <div class="flex -space-x-1.5">
      <img src="../../people-library/assets/portraits/m01-casual-friendly-man-airpods.png" class="w-6 h-6 rounded-full object-cover border-2 border-white" />
      <img src="../../people-library/assets/portraits/f02-young-woman-glasses-tank.png" class="w-6 h-6 rounded-full object-cover border-2 border-white" />
    </div>
    <span class="text-[10px] text-neutral-400">1 hour ago</span>
  </div>
</div>
```

### H4 — Agenda timeline item with progress

```html
<div class="p-3 rounded-xl bg-primary/10 border border-primary/20">
  <div class="flex items-center gap-2 mb-1.5">
    <span class="w-5 h-5 rounded-md bg-primary flex items-center justify-center text-[9px] font-bold text-white">2</span>
    <span class="text-xs font-semibold text-neutral-800">Team Values Discussion</span>
  </div>
  <p class="text-[10px] text-primary ml-7 font-medium">In progress · 5 min left</p>
  <div class="ml-7 mt-1.5 h-1 rounded-full bg-primary/20 overflow-hidden">
    <div class="h-full bg-primary rounded-full" style="width: 60%;"></div>
  </div>
</div>
```

### H5 — Speaker name pill with gradient

```html
<div class="rounded-full flex items-center gap-2 pl-1.5 pr-4 py-1"
     style="background: linear-gradient(135deg, #FF8A9B, #FFB36D);">
  <img src="../../people-library/assets/portraits/f02-young-woman-glasses-tank.png" class="w-7 h-7 rounded-full object-cover border-2 border-white/50" />
  <div>
    <p class="text-[11px] font-bold text-white leading-tight">Alisiya Ken</p>
    <p class="text-[9px] text-white/80">Game test team</p>
  </div>
</div>
```

### H6 — "User wants to join" pill

```html
<div class="flex items-center gap-3 bg-orange-50 rounded-full pl-2 pr-1 py-1.5">
  <img src="../../people-library/assets/portraits/m07-relaxed-man-beard-darkshirt.png" class="w-7 h-7 rounded-full object-cover" />
  <span class="text-xs text-neutral-600 font-medium">Nico wants to join your meeting</span>
  <button class="w-7 h-7 rounded-full bg-orange-500 flex items-center justify-center hover:bg-orange-600 transition-colors">
    <i data-lucide="x" class="w-3.5 h-3.5 text-white"></i>
  </button>
  <button class="w-7 h-7 rounded-full bg-primary flex items-center justify-center hover:bg-primary-dark transition-colors">
    <i data-lucide="check" class="w-3.5 h-3.5 text-white"></i>
  </button>
</div>
```

---

## How to assemble

1. Start with **A1** (3-column shell) or **A2** (full-screen).
2. Drop **B1** (nav rail) into the left column.
3. Stack **B2** + **C1** into the main column.
4. Choose ONE right-panel: **F1** (chat) / **E2** (participants) / **G4** (summary).
5. Enrich video stage with **C2** / **C3** / **D5** / **G2**.
6. Validate against the Quality Bar Checklist (`design-system.md` §8).
