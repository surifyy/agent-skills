# Room UI Templates — Usage Guide

How to take a template from the gallery into a real customer project.

## 1. Use a template as-is (fastest path)

The templates are stand-alone `.html` files. Open in any modern browser:

```
C:\Users\herzhan\.workbuddy\skills\room-ui-templates\templates\01-skyblue-dashboard.html
```

All scripts (Tailwind, Lucide), fonts, and portraits load automatically. **The portraits use a relative path that assumes `room-ui-templates/` and `people-library/` are siblings under `~/.workbuddy/skills/`.**

## 2. Copy markup into a real project

Tailwind utility classes work directly in React, Vue, Svelte, Solid, Astro, vanilla HTML.

**Steps:**
1. **Copy portrait files** into your project's image folder:
   ```
   public/images/people/m04-business-man-blue-shirt.png
   ```
2. **Rewrite `<img src>`**:
   ```html
   <!-- Before --><img src="../../people-library/assets/portraits/m04-...png" />
   <!-- After  --><img src="/images/people/m04-...png" />
   ```
3. **Adopt Tailwind v4** in your project (replace browser CDN with PostCSS/Vite install).
4. **Convert Lucide CDN to a real package**:
   ```jsx
   import { Video, Mic, PhoneOff } from 'lucide-react';
   <Video className="w-5 h-5 text-white" />
   ```
5. **Wire interactivity** — hook each control to your Room SDK handlers (TRTC, Agora, LiveKit, etc.).

## 3. Customize design tokens

Every template uses Tailwind v4's `@theme` block. Change the values once and the entire template re-skins:

```css
@theme {
  --color-primary: #38BDF8;        /* change to brand color */
  --color-primary-dark: #0EA5E9;
  --font-main: 'Plus Jakarta Sans', sans-serif;
  --font-body: 'DM Sans', sans-serif;
}
```

## 4. Replace portraits

- **Customer-supplied photos** — replace `<img src>` paths. Keep `class="object-cover"`.
- **AI-generated portraits** — generate ~5:3 landscape (~1080×648) for hero tile; ~1:1 square for round avatars.
- **Diversify a grid** — templates 07 (2×2) and 09 (3×3) are pre-balanced. Preserve the mix when swapping.

## 5. Composition recipes

| Recipe | Combine |
|---|---|
| Dashboard meeting + AI notes | Video area from `01` + AI-notes panel from `03` |
| Premium board with live captions | Shell from `08` + auto-translator from `05` |
| 3×3 gallery with executive theme | Grid from `09` + dark/gold tokens from `08` |
| Workshop + AI summary | Agenda sidebar from `11` + live-summary from `06` |

## 6. Production checklist

- [ ] Replace skill-relative portrait paths with project paths
- [ ] Replace browser-CDN Tailwind with real install
- [ ] Replace Lucide CDN with framework imports
- [ ] Replace placeholder copy with branded content
- [ ] Wire all toolbar buttons to Room SDK handlers
- [ ] Add `aria-label` to icon-only buttons; check color contrast
- [ ] Test responsively (templates assume ~1380px desktop)
- [ ] Remove third-party brand mentions used as filler
- [ ] Confirm fonts load from your CDN or self-host

## 7. Known limitations

- **Static mockups** — no real WebRTC, no state management.
- **Designed for ~1380px width** — narrower viewports may need additional responsive work.
- **Browser-CDN deps** — pulls Tailwind/Lucide/Fonts from `cdn.jsdelivr.net`, `unpkg.com`, `fonts.googleapis.cn`. Mirror locally before shipping.
- **Portrait demographics** — only 10 portraits exist. Supplement with own assets for broader representation.
