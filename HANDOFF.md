# Handoff → the landing/visual session

From the functionality session. **Everything here is in files you own** — I have not
touched any of them. I've stayed in the modules.

Ownership as I've been working it:

| You | Me |
|---|---|
| `src/sporve-web.host.html` | `src/mod-companies.js` (new) |
| `src/build.py` | `src/mod-payments.js`, `mod-search.js` (CSS scope fix only) |
| the landing page, hero, search bar | the other 7 modules, booking logic, data |
| `assets/` — real imagery | `IMAGE-BRIEF.md` — what to shoot and where it goes |

One shared hazard: **we both run `build.py` against the same `index.html`.** It went
709KB → 948KB → 718KB in twenty minutes as your hero image was inlined and removed.
Whoever builds last wins. If you drop a hero into `assets/`, rebuild before I do.

> ### ⚠️ A fix in `mod-search.js` was overwritten once already
>
> I made exactly one edit in a file of yours — scoping `.se-cmp{min-width:640px}` at
> **mod-search.js:989** (see §4). It was reverted when the file was rewritten from an
> older copy, and I have re-applied it.
>
> **If you have `mod-search.js` open in context from before ~00:45, re-read it from disk
> before you write to it**, or the 640px capsule bug comes straight back. It is a
> four-line change and it is the worst visual defect in the app.

---

## 1. The search bar

> **Superseded — see `LANDING-SPEC.md`.** A full landing-page rebuild brief has since
> landed: white canvas, no dark hero, a three-segment Sport/Location/**Child's age** search
> pill as the signature element, filters moved out of nav and down to the grid. That spec
> replaces this section. What follows is still accurate about *why* the current bar fails,
> and the `#qloc` finding below is load-bearing for either approach.

The owner's note: *"it looks very AI generated and the layout needs to be fixed."*
They're right. Current markup is `heroHTML()` at **host:1736–1745**.

### Two facts worth correcting before you start

- **Enter already works** on the query field — `q.onkeydown` at **host:3394**. Don't
  "fix" that; just don't lose it.
- **`#qloc` is completely unwired.** Grep it: the only hit is the markup at host:1742.
  No `oninput`, no read, nothing. Typing a location does *literally nothing*. On a
  marketplace where all 30 listings are in Miami, the location field is decoration.
  That's a bigger problem than the styling.

### Why it reads as generated

1. **Two unlabelled placeholders in one capsule.** A placeholder dies the moment you
   type. Replace "Miami, FL" and nothing on screen says that field is a location.
   Airbnb, Zillow and Uber all label their segments for exactly this reason.
2. **`style="max-width:130px"` inline on host:1742** — a layout decision living in the
   template, and a magic number. Location gets 21% of the bar, query 70%. For a local
   marketplace that ratio says location is an afterthought — which, per above, it is.
3. **Icon-only 42px circle** carries the primary action with no word on it. It is the
   smallest target in the bar.
4. **Four centered things stacked** — h1, lede, bar, all centered on a centered dark
   panel. This is the canonical generated hero.
5. **The inputs render in a different typeface from the page.** `.searchpill .seg`
   sets `font-size` but never `font-family`, and inputs don't inherit. Every other
   input in the codebase gets `font:inherit` (`.field`, `.msg-compose input`,
   `.cmdinput input`) — the hero search is the one that was missed.
6. **The mobile collapse merges the fields.** At ≤640 the divider is `display:none`
   and both inputs go `flex:1 0 100%` — two placeholders in one white box with no
   separation. `#qloc` also keeps its 130px cap inside a 422px parent, so its hit
   area is a third of the row it appears to occupy.

### Proposed structure

```html
<form class="hsearch" role="search">
  <div class="hsearch-seg">
    <label for="q">What</label>
    <input id="q" placeholder="Sport, coach, or program" value="${esc(S.query)}">
  </div>
  <div class="hsearch-seg">
    <label for="qloc">Where</label>
    <input id="qloc" placeholder="City or ZIP" value="${esc(S.locQuery||"")}">
  </div>
  <button class="hsearch-go" id="qgo" type="submit">
    ${ICON.search}<span>Search</span>
  </button>
</form>
```

```css
.hsearch{
  display:grid;
  grid-template-columns:minmax(0,1.35fr) minmax(0,1fr) auto;
  align-items:stretch;
  width:min(720px,100%);
  padding:6px;
  background:var(--paper);
  border:1px solid var(--rule-strong);
  border-radius:var(--r-l);              /* the card system, not a stock capsule */
  box-shadow:var(--shadow-lift);
  text-align:left;
}
.hsearch:focus-within{box-shadow:var(--shadow-lift),0 0 0 3px var(--slate-ring)}

.hsearch-seg{
  display:flex;flex-direction:column;justify-content:center;gap:2px;
  min-width:0;padding:10px 18px;border-radius:var(--r-m);
  cursor:text;transition:background .15s;
}
/* the seam belongs to the segment, not to an empty <span class="divider"> */
.hsearch-seg + .hsearch-seg{box-shadow:inset 1px 0 0 var(--rule)}
.hsearch-seg:focus-within{background:var(--raise);box-shadow:none}
.hsearch-seg:focus-within + .hsearch-seg{box-shadow:none}

.hsearch-seg label{
  font-size:11px;font-weight:700;letter-spacing:.09em;
  text-transform:uppercase;color:var(--faint);
}
.hsearch-seg input{
  font:inherit;font-size:16px;           /* fixes the typeface break */
  width:100%;min-width:0;padding:0;border:0;background:none;color:var(--ink);
}
.hsearch-seg input:focus{outline:none}   /* the ring lives on .hsearch */

.hsearch-go{
  display:inline-flex;align-items:center;gap:9px;
  padding:0 26px;border-radius:var(--r-m);
  background:var(--ink);color:var(--paper);
  font:inherit;font-size:15px;font-weight:700;white-space:nowrap;
}
.hsearch-go svg{width:17px;height:17px}

@media(max-width:640px){
  .hsearch{grid-template-columns:1fr;padding:8px;gap:6px}
  .hsearch-seg{border:1px solid var(--rule);border-radius:var(--r-m);padding:9px 14px}
  .hsearch-seg + .hsearch-seg{box-shadow:none}
  .hsearch-go{height:50px;justify-content:center}
}
```

### JS this requires (host:3391–3397)

The current handlers assume a click on `#qgo`. With a real form:

```js
const hs=document.querySelector(".hsearch");
if(hs) hs.onsubmit=e=>{e.preventDefault();S.route={name:"explore",arg:null};render();};
const q=document.getElementById("q");
if(q) q.oninput=e=>{S.query=e.target.value;};
const ql=document.getElementById("qloc");
if(ql) ql.oninput=e=>{S.locQuery=e.target.value;};   // ← currently missing entirely
```

Then either filter on `S.locQuery` in `visiblePrograms()` or drop the field. A search
input that discards what you type is worse than no input.

**Also pair it with `.hero-in{text-align:left;align-items:flex-start;max-width:780px}`.**
Un-centering the stack does more to kill the generated read than any change to the bar.

### Dead CSS you can delete

`.searchpill` is no longer in the topbar — only in the hero. ~15 lines of base
`.searchpill` CSS plus `@media(max-width:760px){.searchpill{order:3;flex-basis:100%}}`
are now unreachable except through `.hero .searchpill`.

---

## 2. Functional bugs in the host — ranked

| # | Fix | Where |
|---|---|---|
| 1 | **Every bookable session is dated in the past.** Slots generate `2026-05-xx` against a clock pinned to `2026-08-03`. This silently breaks two things: every cancellation refunds **$0** regardless of the (correct) policy ladder in `mod-payments.js:587-596`, and every booking becomes review-eligible the instant it's paid because the review gate falls back to `date <= TODAY`. One date change fixes both. | host:1052–1064 |
| 2 | **Coach Inbox has no compose box.** A coach can never reply to a family. The rail badge advertises unread messages and the dashboard's "Reply" routes here. Also renders only `S.conversations[0]`, so other threads are unreachable. | host:2594, 2639 |
| 3 | **`bookings` and `reviews` coach tabs render the Business profile form.** Neither has a `coachBody()` branch, so both fall through. The dashboard's "Recent reviews → Reply" lands on a settings form. | host:2203–2204, 2629 |
| 4 | **Business profile form fakes saving.** Fields have no `name`/`id`/handler; Save just toasts "Changes saved" and the value reverts on next render. This is also what `bookings`, `reviews` and Settings all resolve to — the most-hit dead surface in the portal. | host:2629–2647, 3218 |
| 5 | **Sign out doesn't reset `S.portal`.** `render()` short-circuits on `S.portal==="coach"`, so you stay on the coach dashboard and appear still signed in. | host:2982, 3219, 3154 |
| 6 | **"? Support" does nothing in the coach portal.** Same short-circuit — while portal is coach, every route is ignored. | host:2210, 3250, 3154 |
| 7 | **Coach onboarding is unreachable for actual new coaches.** `data-becomecoach` branches on `isVerified()`; a guest gets the host's *other* 3-step modal. The 7-step wizard has no rail entry (`mod-coachonboard.js` exports `views.onboard` but no `tabs:{}`), and no way back once you leave. | host:3301–3306 |
| 8 | **AI Coach parses a budget as an age.** The fallback `\b(\d{1,2})\b` grabs the first 1–2 digit number anywhere. The app's **own example chip** — *"Beginner swimming near Miami under $60"* — parses `$60` as *age 60*, drops the correct kids' listing, and recommends an adults-only program to a parent. Strip the budget before the age match. | host:2113 |
| 9 | **Stale `pendingIntent` fires after an unrelated sign-in.** Dismissing the auth sheet clears `S.modal` but not `S.pendingIntent`. Open "Book", back out, browse, sign in later from the header → the old booking modal ambushes you. | host:3163, 3552 |
| 10 | **Coach trust pills are hardcoded literals** (`Verified` / `cleared` / `connected`), not derived from `pp.status`/`pp.backgroundCheck`/`pp.stripeAccountId`. They contradict `gettingStarted()` at host:2217–2218 for any non-seed profile. | host:2605–2607 |
| 11 | `BUSINESSES[].verified = list[0].verified` rolls verification up **per business from one listing** — the exact inverse of the README's headline claim that checks are per person. | host:1046 |
| 12 | Raw `acct_mockstripe123` rendered verbatim as a caption under "Payouts / Connected". | host:2579 |
| 13 | Latent `TypeError` in the `viewasparent` modal when `S.listings` is empty — which is exactly the state onboarding is meant to produce. | host:2962–2963 |

---

## 2b. Family side — audited, and mostly clean

Swept all 19 family routes in headless Chrome, guest and signed-in, plus a full
modal-coverage diff. Result is genuinely good and worth stating:

- **Every route renders real content.** Zero console errors, zero unevaluated `${`,
  zero `undefined`/`NaN`/`[object Object]` in visible text, across all 38 variants.
- **All 32 modal types resolve to a renderer**, and every one has an opener. No
  orphans in either direction.
- **Close paths are universal** — `$("[data-close],[data-scrim]")` at host:2812 plus the
  Escape handler at host:3170. Pressing X, clicking the scrim, and Escape all work
  everywhere. That was the owner's specific worry and it holds up.

Two real dead ends, both the same shape as the coach-side ones:

| Route | Controls | Problem |
|---|---|---|
| **Schedule** | **0** | Renders real upcoming sessions and nothing is clickable — no open, cancel, or reschedule. Linked from the account menu. |
| **Athlete progress** (`timeline`) | **0** | 1,715 characters of content, entirely inert. |

And one structural note: `render()` ends in `else body=exploreHTML()` (host:3205), so **any
unknown route silently renders Explore** — the same failure mode as unknown coach tabs
falling through to the Business profile form. A `404`/unknown branch would surface these
instead of hiding them.

---

## 3. Visual — ranked

**Dark mode is unreachable.** There is no `@media (prefers-color-scheme: dark)` anywhere,
and no JS ever sets `data-theme`. The `:root[data-theme="dark"]` block is dead code on a
real visit. When forced on, five things break — all the same bug: **a hardcoded white
facing a token that inverts.**

| Element | Breakage |
|---|---|
| `#app` gradient | last stop is hardcoded `rgba(238,241,251,.72)`. Page washes to mid-grey (sampled `(106,108,113)` at the bottom) so dark cards float on a *lighter* field. In light mode it moves the background 3 RGB points — it contributes nothing and destroys dark mode. Delete or tokenise it. |
| `.sporttag` | `rgba(255,255,255,.94)` + `color:var(--ink)` → every sport name on every card invisible |
| `.featrate` | same pattern → the featured card's `★ 4.8` invisible |
| `.searchpill .go` | `color:#fff` + `background:var(--ink)` → primary CTA becomes a blank disc |
| `.trustband .sub` | hardcoded `#B9C2CC` on a band that inverts to near-white |

`#fff` appears **18 times** as a literal. `.sitefoot` and `.mapcanvas` already have correct
dark overrides — so the pattern is understood, these five were just missed.

**Other visual findings:**

- **Sticky offsets.** Topbar is **77px** (76 + 1px border), but `.rail{top:104px}` leaves a
  27px gap and `.bookcard`/`.mapside{top:170px}` leave 93px. Three offsets, none derived
  from the bar. Add `--topbar-h:76px` / `--chrome-h:calc(var(--topbar-h) + 1px)` and express
  the rest as `calc(var(--chrome-h) + 24px)`.
- **Five font weights render identically.** CSS declares 400/500/600/650/700/750/800.
  Measured: 400 and 500 are the same width; **600, 650, 700, 750 and 800 are all the same
  width.** The whole weight hierarchy is a no-op that only looks like a system in source.
  Collapse to 400/700 and get hierarchy from size, colour and spacing.
- **`--display` and `--sans` are byte-identical**, so the rule assigning `var(--display)` to
  `h1,h2,h3,h4,.wordmark,.navlink,.btn…` does nothing. One family, not two. Either give
  `--sans` a real sans stack or delete the token and stop implying a pairing.
- **The resolved face is machine-dependent.** The stack lands on **Rockwell**, which ships
  with MS Office — a Mac without Office falls through to Charter/Georgia and the page becomes
  a different design.
- **27 distinct font sizes** including 7 half-pixel steps that measurably do nothing
  (11.5 vs 12 → identical rendered height; 15.5 vs 16 → identical). Suggest 8 steps:
  11 / 12 / 13 / 14 / 16 / 18 / 22 / 28.
- **16 line-heights**, five of them inside a 6% band. Three would do: 1.1 display, 1.35 UI,
  1.55 prose.
- **14 box-shadow definitions**, 12 of them one-offs.
- **105 emoji instances, 60 distinct**, as product iconography. `.smrow .em{filter:grayscale(1)}`
  is the code apologising for them. There's already a real SVG `ICON` set — extend it.
- **Ragged stat-tile baselines** in the coach header: values sit at y=238, 238, **255**, 238,
  **233**, because one eyebrow wraps to two lines.
- **The only saturated colour on the page** is `.heart.on{color:#FF5A6E}` — within one hex
  digit of Airbnb's Rausch, and hardcoded outside the token set.
- `.trustband .sub` is declared twice; host:738 is immediately overridden by host:739.

---

## 4. Already fixed in modules — don't duplicate

- **`mod-search.js`** — `.se-cmp{min-width:640px}` was written for the compare *table* but
  the same class is used for the per-card compare *button*. All 30 card buttons were
  rendering as blank 640px white capsules bleeding out of their cards. Scoped to
  `.se-cmpwrap .se-cmp`. Verified: 30 buttons, 0 overflowing, 86px each, no page scroll at
  1440/1024/500. **This is the only edit I've made in a file of yours.**
- **`mod-payments.js`** — split-pay could never leave `pending`; nothing anywhere set
  `accepted`, so the share link promised a settlement that couldn't happen. Added a settle
  path and a ledger row.
- **`mod-companies.js`** (mine) — booking confirmations that wrote no record, a hardcoded
  `"Julian Mercer, 13"` age assertion, and consent checkboxes that discarded the answer.
  All now write real records with a computed age gate and versioned consent.

## 5. Images

See **`IMAGE-BRIEF.md`** — generated from the module so it can't drift. 156 images with exact
paths, ratios and shot lists per company.

The pipeline is live: **drop a file at the documented path and it appears.** No rebuild, no
manifest. Fallback is wired in `MOD_COMPANIES.wire()` rather than an inline `onerror`, so a
strict `script-src` won't block it.

```
assets/companies/<companyId>-hero.jpg     coral-hero.jpg
assets/listings/<programId>-hero.jpg      prog_9-hero.jpg
assets/listings/<programId>-g<n>.jpg      prog_9-g0.jpg … -g5.jpg
```

Worth knowing: current card photography is random stock and actively hurts the pitch —
Basketball renders as a bowl of strawberries, Karate as a woman holding a sparkler,
Swimming as a snowy mountain. For a product whose entire premise is verified real coaches,
that costs more credibility than any layout issue on this list.

Two of the six businesses — **Everglade Racquet Institute** and **Sunset Field Athletics** —
have not cleared background checks. Their imagery should stay deliberately plainer so the
photography agrees with "Verification pending" instead of fighting it.
