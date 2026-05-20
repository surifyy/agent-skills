# Path C — Feature Expansion

> Loaded by `../../trtc-onboarding/SKILL.md` when `intent = expand` in `.trtc-session.yaml` (user explicitly said "my existing project already has X, now add Y / 已经接了 X，现在想加 Y").
> Before reading this file, SKILL.md must have populated `.trtc-session.yaml` and passed Stage 1 calibration.

**Your role: Advisor + Implementer.**

## C.1 — Auto-detect existing setup

If file scanning is available, identify which TRTC features are integrated by scanning for Store class usage (`LoginStore`, `DeviceStore`, `LiveListStore`, `BarrageStore`, `GiftStore`, etc.) and populate `project_state.existing_features`.

Present findings as a recap:

> I can see you already have:
> - Login (LoginStore)
> - Live streaming (LiveCoreView + LiveListStore)
> - Device control (DeviceStore)
>
> Not yet integrated: Barrage, Gift, Co-guest, Beauty, Audio effects.

## C-Q1 — Which feature to add

Question text: "Which feature do you want to add next?"

Show only the unintegrated features for the identified product, plus `Type something`. Layout and slice resolution match A2-Q1 (see `reference/path-a2-integrate.md`) but as single-select.

## C.2 — Implementation

After the user picks a feature, delegate to Path A2's step-by-step implementation flow (A2-Q3 per-step confirmation, including the internal apply quality gate). See `reference/path-a2-integrate.md` for the full contract.

## C-Q2 — Suggest related

After the feature is integrated (and has silently passed the internal compile gate), based on `cross_product_relations` and scenario co-occurrence:

Question text: "Related features that often pair well with this one:"

| # | Option |
|---|--------|
| 1-3 | Context-specific suggestions (e.g., after barrage → gift / audience-manage / co-guest) |
| 4 | I'm good for now |
| 5 | Type something |

Picking 1-3 loops back to C.2 implementation. Picking 4 ends onboarding cleanly.
