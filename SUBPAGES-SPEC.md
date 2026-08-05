# Sub-product pages — corrected spec

Supersedes the pasted "Comprehensive Master Prompt" (Gemini). That prompt is
kept honestly in mind here: its *instincts* are good and three of its ideas are
adopted. Its **premise is false**, and building against it would have deleted
working product. This document is what the audit says instead.

---

## 0. The premise, corrected

> "Rebuild and refactor every sub-product page listed under the mega-menu into
> dedicated, high-converting feature landing pages."

There are **no sub-product pages to rebuild**. The mega-menus hold **20 entries
and every one already resolves to a live surface. Zero reach `notFoundHTML()`.**

| Class | Count | Examples |
|---|---|---|
| Live product routes | 11 rows / 10 routes | `product`, `trust` (mod-safety), `companies` (mod-companies, 1042 ln), `explore`, `map`, `messages`, `bookings`, `saved`, `timeline` (mod-reviews), `assistant` |
| Live coach dashboard tabs | 6 | `slots` (mod-coachops), `finances`, `roster`, `notes` (mod-notes, 1023 ln), `media` (mod-media, 1131 ln), `insights` (mod-insights, 890 ln) |
| Live non-page actions | 3 | `becomecoach` (auth → dashboard), `import` (modal), `coachfeatures` |
| **Genuinely absent** | **0** | — |

Six of these are the front end of a 750–1500-line module with its own state,
modals and wiring. "Rebuild them as landing pages" means replacing a working
product with copy *about* the product.

**Nothing in the prompt's page-by-page section gets built as specified.**

---

## 1. What the prompt got right, and what was done about it

| Prompt instinct | Verdict | Action |
|---|---|---|
| These surfaces are under-sold to visitors | **Correct, and the real defect was worse than described** | Fixed — see §2 |
| Alternating light / dark / white section rhythm | **Correct** | Already shipped (`df36ec0`, `6e108f7`); `.band` / `.band.alt` / `.band.dark` |
| Sport emoji badges | **Correct** | Already shipped via `sportGlyph()` |
| Scroll-in section animation | **Correct** | Already shipped, IntersectionObserver + `prefers-reduced-motion` |
| Hover lift `y:-6px` on cards | Correct in spirit | Shipped at −3px with a shadow; −6 with no shadow reads as floating |
| Black bg / white text contrast check | **Correct, and now an enforced invariant** | §3 |

---

## 2. The real defect the prompt was circling

Not missing pages. **Seven menu rows, one destination — for signed-out
visitors.**

The `data-pdest` `tab:` branch set `portal="coach"` and routed to the dashboard
with no auth check; `render()` substitutes `coachLandingHTML()` for anyone
unverified. So Scheduling, Payments, Roster, Session notes, Media & consent,
Insights — plus "Works with how you run" — all delivered the identical page.
It also dropped the family nav on the way out.

Measured before: **6 of 6 rows → 1 distinct page.**
Measured after: **6 of 6 rows → 6 distinct sections**, family portal preserved.

Shipped in `b27c4b8`. `coachLandingHTML()` gained bands for notes, media and
insights (it only covered four of six tabs), each anchored `#coach-<tab>`.

Also fixed: "Instant booking" was byte-identical to "Search by sport & age"
(both `nav:explore`, neither showing a booking flow); `coachfeatures` was a
dead string reaching the right page only by fall-through.

---

## 3. Colour — the prompt's palette is rejected, with measurements

The hard rule from the owner, now an invariant in the stylesheet:
**a black background always carries white or slate text.** On `#000`:
headings `#FFFFFF` (21:1), body `#AEB8C4` (10.45:1), eyebrows `#8B97A5`
(7.07:1), accent `--accent-on-dark #F08A62` (8.52:1), focus ring `#E8EDF3`
(17.84:1). `--accent #C2410C` is **4.06:1 on black and banned there** for
anything but large display text.

The prompt's three accents were measured against the live sport ramp using
CIE76 ΔE (under ~25 reads as the same colour family):

```
#10B981 emerald    vs Golf      #00A15E   ΔE = 11.3    ← disqualifying
                   vs Lacrosse  #009F77   ΔE = 13.0    ← disqualifying
#38BDF8 baby blue  vs Skiing    #0098AD   ΔE = 25.8    ← borderline
#E05A47            vs Basketball#DA5A05   ΔE = 25.4    ← borderline
#E05A47            vs live --accent #C2410C  ΔE = 19.0 ← a real palette change
```

At ΔE 11–13 an emerald "verified / pricing" badge is indistinguishable from the
Golf and Lacrosse **sport marks**, on a page whose premise is that sport colour
means sport. A parent scanning the grid would read a price as a sport tag.

Mapping instead:

| Prompt token | Use the existing |
|---|---|
| `#F1F5F9` Light Slate | `--raise #F7F8FA` |
| `#09090B` Pure Dark | `--ink #000000` via `.band.dark` |
| `#0F172A` headings | `--ink` / `#FFFFFF` on dark |
| `#475569` body | `--muted #3E4753` / `#AEB8C4` on dark |
| `#E2E8F0` borders | `--rule #E3E7EC` |
| `#E05A47` CTA | `--accent #C2410C` |
| `#38BDF8`, `#10B981` | **rejected** — collide with the sport ramp |

**Hazard for any new dark section:** existing components carry
`color:var(--ink)` = `#000`. Dropped into a fresh `background:#09090B` they are
black on black — the inverse of the white-on-white bug fixed in `c6cf658`. New
dark sections go through `.band.dark`, never a raw hex background.

---

## 4. Stack — the prompt's stack does not exist here

React / Next.js / Tailwind / framer-motion / lucide-react are not in this repo
and are not being added. This is one self-contained HTML file built by
`python3 src/build.py`, with a CSP that blocks every external request.
`LANDING-SPEC.md` §0 already documents this translation.

**"Generate router endpoints for all 15 pages" is not buildable as written.**
`pushState`, `popstate` and `location.hash` appear **zero times across all
eleven source files** — every route is in-memory. A URL router is a real
prerequisite, and it is one piece of work, not fifteen.

Equivalents: `framer-motion` → CSS transitions + IntersectionObserver;
`lucide-react` → the existing inline SVG `ICON` set; Tailwind tokens → the
`:root` custom properties.

---

## 5. Content — do not invent

The prompt names "Midwest Elite Hoops" and "Apex Soccer" as live partner
academies. They do not exist. The real six are Apex Performance **Club**, Coral
Reef Aquatics, Downtown Hoops Academy, Everglade Racquet Institute, Ironside
Combat Gym, Sunset Field Athletics — 30 programs, Miami.

"Interactive stats counters for active leagues" describes a product Sporve is
not. There are no leagues; the wedge is booking a background-checked person.

Every public figure is computed from `PROGRAMS` at render time, never typed.

---

## 6. Labels that over-promise (open)

Found during the audit, not yet fixed:

1. **"Client roster"** promises "every family, session, and note in one place";
   the tab renders a trainer list plus one hardcoded team with a single athlete.
2. **"Payments & payouts"** promises payouts; the tab shows a hardcoded 9% fee
   table and "Payouts: Not set up". The real 1497-line `mod-payments` registers
   `wallet`, which **no menu entry points at**.
3. **"Scheduling & availability"** lands on the tab the rail calls "Recurring
   slots" — availability rules, not the day view.
4. **Bookings / Messaging / Athlete progress** show sign-in empty states to
   guests rather than the promised surface.

---

## 7. Order of work

1. ~~Give every coach menu row a distinct signed-out destination~~ — done, `b27c4b8`.
2. Point a menu entry at `wallet`, or retitle "Payments & payouts" to match the tab.
3. Guest previews for the four sign-in-walled family rows.
4. Hash router + `popstate` — the actual prerequisite for any indexable page.
   Only after this does "feature landing pages for SEO" become a coherent ask.
5. Split `productHTML()`'s two grids into anchored sections so the About row deep-links.
6. `index.html` is 1.34 MB. Weigh before adding inline media.

**The one honest argument for the original prompt** is SEO: 20 in-app routes are
one indexable URL. The prompt never makes that argument — and it costs a router
first (item 4), not fifteen page templates. Cheapest test before building any of
it: ship the anchored coach page and count menu-click → "Become a coach" starts.
If conversion does not move, the pages were not the bottleneck either.
