---
name: trtc-search
description: >
  Discovers matching slices from the TRTC knowledge base given a natural-language
  query. Use when onboarding or docs needs to find slice IDs for a feature
  description, symptom, error code, or pattern query. Accepts (product, platform,
  query, intent) and returns matched slices with confidence and source attribution.
  Not user-facing — callers compose the final answer from returned results.
---

# TRTC Knowledge Base Search

You search the TRTC knowledge base to find relevant atomic capabilities (slices) and integration scenarios. You handle multi-product, cross-platform searches with a structured strategy chain and return a machine-readable response.

---

## Response Contract (read this first)

Every call returns exactly this shape. The calling skill (`docs` / `onboarding`) reads fields by name — do NOT improvise the format, do NOT collapse fields into prose.

```yaml
response:
  status: matched | no_match | no_slice | ambiguous_product | status_planned
  matches:                             # populated when status ∈ {matched, status_planned}; empty otherwise
    - slice_id: <product/ability>      # e.g. live/barrage
      confidence: high | medium | low
      match_strategy: exact | tag | product-keyword | cross-related | fuzzy
      content_loaded: full | summary | index-only
      file_paths_read: [...]           # actual file paths opened this turn (relative to repo root)
      related: [...]                   # one-hop related slice_ids NOT already in matches
  ambiguous_candidates: [...]          # populated ONLY when status = ambiguous_product, e.g. [live, chat]
  reason: "..."                        # populated ONLY when status ≠ matched; one-sentence cause
```

### status semantics

| status | Meaning | matches | ambiguous_candidates | reason |
|--------|---------|---------|----------------------|--------|
| `matched` | ≥ 1 slice found with usable content | non-empty | — | — |
| `status_planned` | slice exists in index but content not yet written | non-empty, `content_loaded: index-only` | — | "slice `<id>` is status: planned" |
| `no_slice` | product exists but has zero slices in KB (e.g., Call, Conference at early stage) | empty | — | "product `<id>` has no slices in KB" |
| `no_match` | search ran to exhaustion without finding relevant slices | empty | — | one-line cause (e.g., "error code 99999 not in any slice.error_codes or body text") |
| `ambiguous_product` | product was null AND fuzzy-only hits span multiple products | empty | non-empty (e.g., `[live, chat]`) | "query plausibly matches multiple products; ask user" |

### confidence → match_strategy mapping

Confidence is derived from match_strategy, not judged separately:

- `high` ← `exact` or `tag`
- `medium` ← `product-keyword` or `cross-related`
- `low` ← `fuzzy`

Callers should use `confidence` for quick guards (e.g., `if response.matches[0].confidence == 'high': answer from slice, skip llms.txt`) and `match_strategy` for traceability when debugging.

### What callers do with each status

- `matched` → read `matches[].file_paths_read`, compose answer from slice contents.
- `status_planned` → show the slice's index-level description; fall through to caller's fallback (docs → llms.txt).
- `no_slice` / `no_match` → caller falls back to its own escape route (docs: llms.txt lookup; onboarding: ask user / degrade).
- `ambiguous_product` → caller asks the user which of `ambiguous_candidates` they mean, then re-calls search with the confirmed product.

---

## Inputs (from calling skill: `docs` or `onboarding`)

- **product**: Identified product (chat/call/rtc-engine/live/conference), or `null` if ambiguous
- **platform**: Identified platform (web/android/ios/flutter/electron), or `null`
- **query**: The user's original question / keywords
- **intent**: one of the values listed below.

> **Authoritative enum**: this file is the canonical source for the set of `intent` values search accepts. Callers (`docs`, `onboarding`) MUST only pass a value from this list and MUST map their own domain intent (e.g. docs' `slice-lookup`, onboarding's Path B free-text symptom) to one of these four. When this list changes, callers update their mapping tables. The list:

- `error-code` — from `docs`: query contains a numeric error code. Prioritize `exact`; on miss, run full-text digit search before other strategies.
- `pattern` — from `docs`: user asks for the official pattern of X, or compares X vs Y. Prioritize `tag`.
- `feature` — from `docs` (implementation method lookup) or `onboarding` (user described a feature in natural language): need to find the corresponding slice ID. Prioritize `tag` / `product-keyword`. When multiple slices match, return summaries (`content_loaded: summary`) for the caller to present as a selection list.
- `troubleshoot` — from `onboarding` Path B: user described a symptom in free text, need to find the slice(s) with relevant troubleshooting content. Match against slice troubleshooting sections and in-file `error_codes` sections.

---

## Search Workflow

### Step 1: Read the index

Read `knowledge-base/index.yaml` to get the catalog. Fields present at the index level:

- **products**: `id`, `name`, `description`, `llms_file` (`llms_file` is used by the `docs` skill, not by search)
- **cross_product_relations**: `id`, `products`, `slices`, `description`
- **slices**: `id`, `name`, `tags`, `platforms`, `file`, `description`, `status`
- **scenarios**: `id`, `name`, `slices`, `file`, `description`, `status`

> **Fields NOT in index.yaml** (common misconception — don't assume them on the index):
> - `error_codes` — lives inside the slice file body as an `## 错误码` / `## error_codes` section. To check it, the `file` path must be read.
> - `related` — same: lives inside slice file frontmatter/body, not in index.
> - `platform_files[platform]` — there is no such index field. Platform-specific content lives at `slices/{product}/{platform}/{ability}.md` on disk. To check availability, try reading that path; if it doesn't exist, there is no platform-specific slice for that pairing.

> **Out of scope**: do NOT read llms files, do NOT fetch official doc URLs. If the caller needs a doc URL (e.g., fallback when no slice matches an error code), return `status: no_match` and let the calling skill (`docs`) do the llms.txt lookup.

### Step 2: Five-Strategy Matching (by priority)

Try strategies in order; collect matches. Earlier strategies have higher priority. Higher priority wins on rank; ties broken by tag-intersection count.

| # | match_strategy | Triggers on | How to match |
|---|---------------|-------------|--------------|
| 1 | `exact` | query contains a numeric error code, a known slice_id like `chat/multi-instance`, or a scenario_id | (a) If an error code: look inside each slice's `file` for its `## 错误码` / `## error_codes` section and match the code. On `intent=error-code` miss, additionally grep all slice file bodies for the digit sequence (covers codes mentioned in troubleshooting prose). (b) If a slice_id or scenario_id: direct lookup in index arrays. |
| 2 | `tag` | after exact (or alongside when no error code) | Extract keywords from the query (LLM does Chinese↔English bidirectionally on its own; consult the "Keyword Hints" table below only for non-intuitive SDK naming). Intersect with each slice's `tags`. Rank by intersection count. |
| 3 | `product-keyword` | `product` is set AND tag didn't produce a high-confidence hit | Within that product's slices, fuzzy-match against `name` (higher weight) and `description`. Both Chinese and English terms. |
| 4 | `cross-related` | `tag` or `product-keyword` produced a partial hit AND either (a) query contains signals of a second product, or (b) the initial hit set feels incomplete | Expand via `cross_product_relations` entries whose `products` overlap, OR follow the already-matched slice's `related` list (read from slice file) for one hop. Fold those into matches at medium confidence. |
| 5 | `fuzzy` | no strategy 1-4 produced anything | Last-resort: use Keyword Hints for bidirectional expansion, match against scenario `name` + `description`, or match slice `description` without tag overlap. All hits are `confidence: low`. |

#### Intent-driven priority adjustments

| intent | Priority hint |
|--------|---------------|
| `error-code` | `exact` runs first; on miss AND `intent=error-code`, run full-text digit grep before strategy 2. Return immediately on strategy-1 hit. |
| `pattern` | Run all strategies, but rank `tag` hits above `product-keyword`. |
| `feature` | `tag` and `product-keyword` prioritized. If ≥ 4 matches total, downgrade all `content_loaded` to `summary` so the caller can present a selection. |
| `troubleshoot` | Prefer slices whose body has a troubleshooting section relevant to the described symptom. Check in-file `error_codes` and 排障 sections when reading for rank. |

#### product=null degradation

When `product` is `null`:

- Strategies `exact` and `tag` run normally (they don't need product). If either yields a `confidence: high` hit, return `status: matched` — do NOT trigger ambiguity.
- `product-keyword` is skipped (it requires product).
- `cross-related` and `fuzzy` run as full-catalog searches, capped at **5** matches, ranked by tag-intersection count (ties: `name` match > `description` match).
- If all remaining results are `confidence: low` (fuzzy only) AND they span ≥ 2 products, return `status: ambiguous_product` with `ambiguous_candidates` listing the distinct products seen. DO NOT return low-confidence results — force the caller to disambiguate first.
- If fuzzy hits stay within one product, return them normally as `matched`.

### Step 3: Platform Filtering

If `platform` is specified:

- Filter results to slices whose `platforms` array contains the requested platform.
- Keep cross-platform overviews (slices present at `slices/{product}/{ability}.md` with no platform subpath) as secondary results — they're generally useful.
- Framework-to-platform mapping (applied at the caller's layer but repeated here as reference):
  - React / Vue → Web
  - Kotlin → Android
  - Swift / Objective-C → iOS
  - Dart → Flutter

If the user needs code but hasn't specified a platform, surface that fact via `reason` (`"platform required for code example"`) — the caller asks.

### Step 4: Progressive Content Loading

Set `content_loaded` per match based on result-set size:

- **Top 1-3 matches in `matches[]`** → read the full slice file at `knowledge-base/{slice.file}`; if a platform-specific file exists at `knowledge-base/slices/{product}/{platform}/{ability}.md`, read that too. Set `content_loaded: full`.
- **4+ matches** (typical on `intent=feature` ambiguity) → do NOT read each file; return index-level fields only (name, description, tags). Set `content_loaded: summary`. Let the caller present a selection.
- **Slice with `status: planned`** → do NOT try to open its `file` (it likely doesn't exist yet). Use the index description. Set `content_loaded: index-only` and set top-level `status: status_planned` on the response.

Record every file actually read in `matches[].file_paths_read`. This is the caller's canonical source for "which files grounded the answer".

### Step 5: Build the response

Fill the Response Contract based on Step 2-4 results:

| Situation | response.status | matches | extras |
|-----------|----------------|---------|--------|
| Strategies 1-5 produced content-loadable hits | `matched` | populated; confidence derived from match_strategy | — |
| Hits all pointed at planned slices | `status_planned` | populated with `content_loaded: index-only` | `reason: "slice <id> is status: planned"` |
| product exists in index but has zero slices | `no_slice` | empty | `reason: "product <id> has no slices in KB"` |
| product=null AND only fuzzy hits spanning ≥ 2 products | `ambiguous_product` | empty | `ambiguous_candidates: [...]`, `reason: "..."` |
| Strategies exhausted, nothing relevant at any confidence | `no_match` | empty | `reason: "..."` (be specific — error code not found / no tag overlap / etc.) |

> **Display rules live with the caller**, not with search. search only reports `file_paths_read`; it does not dictate how the caller quotes code, when to include snippets, or how to render confidence. See `../trtc-docs/SKILL.md` Step 3 and `onboarding/reference/path-a2-integrate.md` slice-loading block for those rules.

---

## Keyword Hints (non-intuitive mappings only)

Bidirectional Chinese↔English translation for common vocabulary is delegated to the LLM — it already understands that "弹幕" ≈ barrage/danmu, "美颜" ≈ beauty, "进房" ≈ enter-room. This table lists **only mappings that are NOT obvious from translation alone** — cases where the user's colloquial term differs from the SDK's internal naming.

| User phrasing | SDK tag / keyword | Why it needs a hint |
|---------------|--------------------|---------------------|
| 互踢 | `kick-offline`, `multi-instance` | Not an SDK term; the root capability is multi-instance login conflict |
| PK | `battle`, `BattleStore` | "PK" is colloquial; SDK names it battle |
| 黑屏 | `setLiveID`, `black-screen` | The usual root cause is a missed `setLiveID` call, not obvious from "black screen" |
| 跨房连线 | `co-host`, `CoHostStore` | SDK-proprietary term |
| 连麦 | `co-guest`, `seat`, `CoGuestStore` | SDK uses `co-guest`, not the more literal `co-mic` |
| 踢人 | `kick`, `kickUserOutOfRoom` | Exact method name is non-intuitive |
| 音效 | `audio-effect`, `changer`, `reverb`, `ear-monitor` | Multiple sub-capabilities under one colloquial term |
| 观众 | `audience`, `LiveAudienceStore` | Associated Store name is not what a user would guess |

For any phrasing NOT listed: let the LLM do its own Chinese↔English bridging, then match against `tags` / `name` / `description` directly. Do NOT expand this table defensively with obvious translations — it only pays for its maintenance cost on the non-obvious ones.

---

## Edge Cases

### Missing content

| Scenario | status | Handling |
|----------|--------|----------|
| Product exists in index but has no slices (e.g., call, conference at early phase) | `no_slice` | `matches: []`, `reason: "product <id> has no slices in KB"` — caller (docs) falls back to llms.txt |
| Matched slice has `status: planned` in index | `status_planned` | `matches[].content_loaded: index-only`, use index description; caller decides fallback |
| Platform requested but no platform-specific file at `slices/{product}/{platform}/{ability}.md` | `matched` | Return product-level overview with `content_loaded: full`, `reason: "no platform-specific file for <platform>"` — caller tells the user in their own language that the platform-specific code example isn't yet in the KB; do NOT synthesize code |

### Cross-product questions

| Scenario | Handling |
|----------|---------|
| "直播+弹幕" (Live+Chat) | `tag` hits live/* + query contains chat signal → `cross-related` expands via `cross_product_relations` → matches include slices from both products |
| "视频通话+聊天" (Call+Chat) | Same pattern: `tag`/`product-keyword` initial hits + `cross-related` expansion |
| "该用哪个产品？" | Out of scope — return `no_match` with `reason: "product-selection question, not a slice lookup"`; caller (root / onboarding) handles product identification |

### Search ambiguity

| Scenario | Handling |
|----------|---------|
| Vague single-term query like "消息" with product=null | `tag` returns many chat/* hits → `matched` with `content_loaded: summary` for the top 3-5; caller presents selection |
| Mixed Chinese-English "怎么 kick offline" | LLM bridges "kick offline" → Keyword Hints row for 互踢 → `tag` match |
| Only an error code like "6208" | `exact` (strategy 1) → `matched`, confidence `high` |
| Error code not in any slice | `no_match`, `reason: "error code <code> not in any slice.error_codes or body text"` — caller (docs) falls back to llms.txt |

### Platform edge cases

| Scenario | Handling |
|----------|---------|
| Conceptual question, no platform needed | Return product-level overview only; `platform` argument can be null |
| Needs code but no platform specified | Return `matched` with whatever was found; set `reason: "platform required for code example"` — caller asks |
| React/Vue → Web, Kotlin → Android, Swift/ObjC → iOS, Dart → Flutter | Caller normalizes; search accepts the normalized platform |
