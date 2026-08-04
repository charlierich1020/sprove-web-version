# Landing page rebuild — spec

Same brief, translated to the stack we actually have. Supersedes §1 of `HANDOFF.md`
(the search-bar patch), which was a repair of the old hero. This replaces it instead.

**Owner: the landing/visual session.** The landing page is `heroHTML()` + `landingHTML()`
in `src/sporve-web.host.html`. Under our split that file is theirs. I have not touched it.

## 0. Stack translation

| Brief assumes | Build against |
|---|---|
| Next.js + TS + Tailwind + Supabase | Vanilla JS. One file. `src/sporve-web.host.html`, rebuilt via `python3 src/build.py` |
| A token file | The `:root{}` block, `sporve-web.host.html:10–56`. Edit tokens there |
| Supabase queries | `const RAW = [...]` (host:988–1019) → `PROGRAMS` (host:1022). 30 rows, 6 businesses |
| React components | Template-literal functions returning HTML strings; wired by `data-*` in `wire()` |
| Tailwind classes | Hand-written CSS in the same `<style>` block |

No data layer needs building — `PROGRAMS` already carries `sport, minAge, maxAge, price,
rating, reviews, lat, lng, verified, cap, enrolled`. Distance is already solved:
`mod-search.js` has a real haversine against `ORIGIN = Miami, FL`.

## 1. Token deltas required

Add to `:root{}`:

```css
--accent:#C2410C;        /* see note — NOT persimmon */
--accent-ink:#9A3412;    /* hover/active */
--accent-tint:#FDF0E9;   /* active chip fill */
--r-ctl:10px;            /* control  */
--r-card:16px;           /* card     */
--r-pill:999px;          /* pill     */
--pad-s:64px; --pad-m:96px; --pad-l:128px;
```

**On the accent.** The brief says Persimmon. Persimmon (~`#EC5800`) sits inside the sport
ramp — Basketball is `#DA5A05`, Climbing `#CE6600`, Football `#C27000`. A brand accent in
that band reads as "the basketball colour" on a page whose whole premise is that sport
colour means sport. Two ways out, pick one:

1. **Shift the accent out of the ramp** — `#C2410C` (burnt, darker and redder than any sport
   token) or go the other way to a deep teal `#0E7490`, which no sport uses.
2. **Keep Persimmon and desaturate the sport ramp** to greys-with-a-hint, so colour means
   brand and sport marks are shape-coded instead.

I've written (1) above because it's the smaller change. Flag it if you want (2).

**Delete on sight:** the `#app` background gradient (host `#app` rule) — its last stop is a
hardcoded near-white that contributes 3 RGB points in light mode and destroys dark mode.
The brief's white-canvas rule makes it dead weight anyway.

Radii audit target: every rounded element resolves to `--r-ctl`, `--r-card`, or `--r-pill`.
The existing `--r-s/--r-m/--r-l/--r-xl` (8/12/16/22) is four values — collapse it.

## 2. Typography — the contract is unenforceable until the faces are embedded

The brief names Oswald (display) and Hanken Grotesk (body). **Neither is loaded.** The CSP
blocks font CDNs, so `<link>` to Google Fonts silently falls back and the page *looks* like
the contract was followed when it wasn't. Today the stack resolves to **Rockwell** — an MS
Office font, so the design isn't even reproducible across machines.

Two honest options:

1. **Embed both as Latin-subset woff2 data URIs.** ~35–45KB each, no network, survives the
   CSP. This is the only way the two-family contract is real.
   ```css
   @font-face{font-family:"Oswald";src:url(data:font/woff2;base64,…) format("woff2");font-display:swap}
   --display:"Oswald",Impact,"Haettenschweiler",sans-serif;
   --sans:"Hanken Grotesk",system-ui,-apple-system,"Segoe UI",sans-serif;
   ```
2. **Drop to one family** and get hierarchy from size and weight. Honest, and better than a
   fake pairing.

**Do not** ship `--display` and `--sans` resolving to the same stack, which is the current
state — the rule assigning `var(--display)` to `h1,h2,h3,h4,.wordmark,.navlink,.btn` is
currently a no-op.

**Weight warning:** the CSS declares 400/500/600/650/700/750/800. Measured, **600, 650, 700,
750 and 800 all render identically**; 400 and 500 render identically. Seven declared weights,
two actual. Under the new contract use exactly 400 and 700 unless a variable font is embedded.

Six steps, no seventh:

| Step | Size | Face | Used by |
|---|---|---|---|
| display | `clamp(38px,4.6vw,58px)` | display | hero H1 only |
| h2 | 30px | display | top-level section headings only |
| h3 | 19px | body | grid header, card names |
| body | 16px | body | prose, inputs |
| small | 14px | body | card meta, trust line |
| micro | 11.5px `.08em` caps | body | labels, eyebrows |

Current state is **27 distinct sizes** including seven half-pixel steps that measurably do
nothing (11.5 vs 12 → identical rendered height). All of them go.

## 3. Section stack

```
┌ NAV ─────────────────────────────────────────────────────────┐
│ SPORVE                    Become a coach   ( avatar )        │  white, hairline base
├ HERO ── max 55vh, white, no image ───────────────────────────┤
│   Book a background-checked coach for your kid.   [display]  │
│   Any sport. Real coaches, verified. Booked in minutes.      │
│   ┌──────────┬───────────┬──────────┬───┐                    │
│   │ Sport ▾  │ Location  │ Kid's age│ ● │  ← signature       │
│   └──────────┴───────────┴──────────┴───┘                    │
│   ✓ background-checked · ✓ payments protected · ✓ free 24h   │
├ SPORT RAIL ── 8–10 tiles, h-scroll, 3px sport underline ─────┤
├ GRID ── "Coaches near Miami, FL"            See all 30 →     │
│   [chips] Background-checked · Under $50 · Single · Monthly  │
│   ▢ ▢ ▢ ▢   ← 4 cols, top row visible at 1440×900            │
├ HOW IT WORKS ── 1 Search · 2 Compare · 3 Book · <300px ──────┤
├ PROOF ── one parent quote (+ stats only if true) ────────────┤
├ COACH ── "Coach on Sporve", outline button, slate-50 ────────┤
└ FOOTER ── 4 cols, hairline top ──────────────────────────────┘
```

### Nav — resolve this first

The brief says remove **Product**, **Filters**, the sport dropdown, and the Family/Coach
toggle from global nav. That **reverses the earlier instruction** that produced the current
*Product · Filters · Saved* subnav, which is live.

If the brief wins: `subnavHTML()` is deleted or reduced, `productHTML()` loses its nav entry
(keep the route — it's real and reachable from the footer), and `data-openfilters` moves down
to the grid. Filters belong to the grid they filter.

Right side, four elements max: `Become a coach` (text) + avatar. That's two — good.

### Hero

- **No dark panel.** Delete the `.hero-panel` gradient block entirely, don't restyle it.
  It's the canonical §8.9 violation: a viewport-height region with no meaningful content.
- **No image.** Photography arrives in the cards.
- `max-height:55vh`, left-aligned. `.hero-in{text-align:left;align-items:flex-start;max-width:780px}`.
  Un-centring the stack does more to kill the generated read than anything else here.

### The signature element — the three-segment pill

Spend the boldness here, keep everything else quiet. The **age segment is the differentiator**:
it tells a parent this is about their kid, not a venue booking.

```html
<form class="hs" role="search">
  <div class="hs-seg"><label for="q">Sport</label>
    <input id="q" list="hs-sports" placeholder="Any sport" autocomplete="off"></div>
  <div class="hs-seg"><label for="qloc">Location</label>
    <input id="qloc" placeholder="Miami, FL"></div>
  <div class="hs-seg hs-age"><label for="qage">Child's age</label>
    <select id="qage"><option value="">Any age</option>…6–18…</select></div>
  <button class="hs-go" type="submit" aria-label="Search">${ICON.search}</button>
</form>
```

```css
.hs{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr) minmax(0,.8fr) auto;
  align-items:stretch;width:min(760px,100%);padding:6px;background:var(--paper);
  border:1px solid var(--rule-strong);border-radius:var(--r-pill);box-shadow:var(--shadow-lift)}
.hs:focus-within{box-shadow:var(--shadow-lift),0 0 0 3px var(--slate-ring)}
.hs-seg{display:flex;flex-direction:column;justify-content:center;gap:2px;min-width:0;
  padding:10px 20px;border-radius:var(--r-pill);cursor:text;transition:background .15s}
.hs-seg + .hs-seg{box-shadow:inset 1px 0 0 var(--rule)}
.hs-seg:focus-within{background:var(--raise);box-shadow:none}
.hs-seg:focus-within + .hs-seg{box-shadow:none}
.hs-seg label{font-size:11.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--faint)}
.hs-seg input,.hs-seg select{font:inherit;font-size:16px;width:100%;min-width:0;padding:0;
  border:0;background:none;color:var(--ink);appearance:none}
.hs-seg input:focus,.hs-seg select:focus{outline:none}
.hs-go{width:52px;height:52px;border-radius:var(--r-pill);background:var(--accent);color:#fff;
  display:grid;place-items:center;align-self:center;justify-self:end;margin-right:2px}
.hs-go:hover{background:var(--accent-ink)}
@media(max-width:720px){
  .hs{grid-template-columns:1fr;padding:8px;gap:6px;border-radius:var(--r-card)}
  .hs-seg{border:1px solid var(--rule);border-radius:var(--r-ctl);padding:9px 14px}
  .hs-seg + .hs-seg{box-shadow:none}
  .hs-go{width:100%;height:50px;border-radius:var(--r-ctl)}
}
```

**Labels are mandatory.** A placeholder dies the moment you type — that is the single
biggest reason the old bar read as generated.

**JS that must change** (host:3391–3397). Today `#q` works and **`#qloc` has no wiring at
all** — its only appearance in the codebase is the markup line. Typing a location does
literally nothing.

```js
const hs=document.querySelector(".hs");
if(hs) hs.onsubmit=e=>{e.preventDefault();S.route={name:"explore",arg:null};render();};
const q=document.getElementById("q");     if(q)   q.oninput  =e=>{S.query=e.target.value;};
const ql=document.getElementById("qloc"); if(ql)  ql.oninput =e=>{S.locQuery=e.target.value;};
const qa=document.getElementById("qage"); if(qa)  qa.onchange=e=>{S.ageQuery=e.target.value?Number(e.target.value):null;};
```

Then filter on all three in `visiblePrograms()`. `S.ageQuery` maps straight onto
`p.minAge <= age <= p.maxAge`. A search input that discards what you type is worse than
no input.

### Card anatomy — six facts, fixed order

`cardHTML()` already emits most of this. Deltas:

| Brief | Now | Action |
|---|---|---|
| Photo 4:3 | `aspect-ratio:20/19` | change to `4/3` |
| Sport chip · **age range** · **distance** | sport chip only | add `Ages ${p.minAge}–${p.maxAge}`; distance via `MOD_SEARCH` haversine |
| `Next: Sat 9 AM` | absent | **blocked** — every slot is dated `2026-05-xx` against a clock pinned to `2026-08-03`. Fix `SESSIONS`/`slotsFor()` (host:1052–1064) first or omit the row |
| Whole card is the link, no buttons inside | compare button injected into every card | see below |
| Hover raise, image ≤1.03 | `scale(1.045)` | change to `1.03` |

**Blocking bug in the card footer:** `mod-search.js` injects a Compare button into every
card, and `.se-cmp` names both that button *and* the compare table. The table's
`min-width:640px` lands on all 30 buttons, rendering them as blank 640px capsules bleeding
out of every card. I've scoped it to `.se-cmpwrap .se-cmp` — **it was overwritten once
already, so re-read `mod-search.js` from disk before writing to it.** Under the brief's
"no buttons inside cards" rule, that button should move out of the card entirely.

Verification badge: 20 of 30 listings are verified. Everglade Racquet Institute and Sunset
Field Athletics have **not** cleared checks — they must render "Verification pending", never
the shield. That rule already holds in `cardHTML()`; keep it.

### Grid header counts

`See all 30 →` must come from `PROGRAMS.length`, not a literal. The count and the list share
one source or they will drift.

## 4. States

Existing gaps to close: focus-visible is global (`:focus-visible{outline:2px solid var(--slate);
border-radius:4px}`) but draws a 4px-radius square around pill-shaped controls — scope a
`--r-pill` variant. Skeleton cards must match the real anatomy (4:3 photo block + 4 text
lines), not spinners.

Empty state copy: `No coaches for [sport] near [location] yet.` + `Widen the search area` /
`Get notified when one joins`.

## 5. Prohibition self-check

| # | Why the plan complies |
|---|---|
| 1 | Dark hero panel is deleted, not restyled. Canvas is `--paper` throughout |
| 2 | `#app` gradient deleted. No glow/glass/orbs anywhere in the stack |
| 3 | Faces embedded as woff2 data URIs, or one family honestly — never a silent fallback |
| 4 | No Tailwind or shadcn in this repo; every colour is already a `:root` token |
| 5 | "How it works" is three numbered lines of text, no icon boxes |
| 6 | One filled button per viewport: hero = search submit; coach band = outline; rest = text links |
| 7 | Radii collapse 4→3; type 27→6 |
| 8 | Proof band ships the quote alone unless a stat is true. No invented numbers |
| 9 | 55vh hero carries H1 + search + trust line — the old empty dark region is gone |
| 10 | Filters move from nav to the grid they filter |

## 6. Compromises to report

1. **Persimmon collides with the sport ramp** — accent shifted to `#C2410C`. Decide or override.
2. **The nav rule reverses a previous instruction** that produced the live Product/Filters/Saved subnav.
3. **`Next: Sat 9 AM` cannot ship** until the seeded session dates move past 2026-08-03.
4. **Fonts are unenforceable** without embedding; today the stack resolves to Rockwell.
5. **No Supabase.** Data flows from `RAW` → `PROGRAMS`, which is the existing data layer here.
