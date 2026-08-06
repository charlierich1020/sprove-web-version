# the-sporve-web — standing rules

Derived from 170 of the owner's own messages across the last 7 days. Each rule
below is here because he had to say it more than five times.

## 1. A task is not done until it is deployed and verified live

The most repeated instruction in the corpus, ~10 times: *"update everything to
sporve.vercel aswell as the github repo"*, *"make sure these are all implemented
then make sure it's live updated in vercel"*.

After any user-visible change: build, commit, push, wait for the Vercel deploy,
then **verify against the production URL** and end the turn with that URL.
Never report "done" from a local build.

**Verify the right way.** This page renders from template literals, so a string
like `coach-insights` is generated at runtime and **never appears in the served
HTML**. Grepping for it will fail forever and look like a broken deploy — that
happened, and cost two timeouts. Verify by either:

- grepping a **source** marker (`bizVerified`, `data-sporttoggle`, `mqpause`), or
- comparing `wc -c` of the live response against local `index.html`, or
- driving the live page and asserting on the rendered DOM.

## 2. Change only what was asked

~7 times: *"do not change too much with the app"*, *"keep much all the
information the same but rearrange"*.

Do not restructure, rename, reword or improve adjacent code, copy or layout. If
the change appears to require touching something outside its scope, stop and
ask. List every file touched at the end of the turn.

## 3. Colour law

~6 times, and stated as an absolute: *"DO NOT CHANGE the brand color palette"*,
*"black background always have white or slate text"*.

- Black, white and slate are frozen. They carry all chrome and are never restyled.
- **Text on a black ground is white or slate. Never a token that can resolve
  dark** — `--paper` inverts under `data-theme="dark"` and has produced
  near-black-on-black. Use literals in `.band.dark`.
- `--accent #C2410C` measures **4.06:1 on black** and is banned there for
  anything but large display text. Use `--accent-on-dark #F08A62` (8.52:1).
- Sport colours are **accent-only**: tag, glyph, dot, 3px identity bar. Never a
  card background, never generic chrome, never body text — the ramp measures
  3.35–3.95:1 as label type. Use `sportInk()` when a sport colour must be text.

The reference site `sporve.vercel.app` uses this same system: its slate
`#F7F9FF` is ΔE 2.1 from `--raise`, its black `#0A0C0F` is ΔE 3.6 from `--ink`,
and every chromatic colour on it is a sport token. Briefs proposing
`#E05A47`/`#38BDF8`/`#10B981` are approximating what is already here.

## 4. Fan out to subagents

~8 times: *"have the agents hekp you run through the remainder"*. For any
multi-part task, run subagents in parallel rather than serially, and say which
agent produced which finding.

Two operational notes learned the hard way: **pin a snapshot** of the source
before launching read-only auditors, because editing files while they read
stalls them; and **tell them to `rg -l` then read line ranges**, because
pointing an agent at a 208-file repo without that reliably times it out.

## 5. Teach as you go — explain every edit

Stated directly: *"Make sure that the agent helps me learn exactly what is
going on after each edit."*

After each change, say in plain language: **what changed, why, and what it
means for the page.** Not a diff summary — the reasoning. If a judgement call
was made (a value held back, a spec item interpreted rather than followed
literally), say which and why, so the owner can overrule it.

The owner did not write this code. A change he cannot follow is a change he
cannot review, and an unreviewable change is how the wrong thing ships twice.

## 6. Check a spec's premises before building on them

Pasted briefs have repeatedly asserted things that are not true of this repo —
fonts that are not embedded, reference files that do not exist, a package
manager that is not installed, hex values approximating tokens already here.
Verify every load-bearing claim against the repo BEFORE writing code, and
report the mismatch rather than silently building on it or silently ignoring
it. A spec that reverses a decision the owner made earlier is the most
important case: surface it, do not just pick one.

## 7. When the owner has to act, give click-level steps

~7 times: *"this still to vauge, tell me exactly where to go, what to click"*.
Exact URL, exact button label, full copy-paste-ready values. No "navigate to
your project settings".

---

## Before you commit

```bash
bash src/smoke.sh
```

Exit 0 = safe. It checks: the build emits, both faces inline, the host script
boots, no JS errors on 13 visitor-reachable routes, the dark-ground invariant
holds, no horizontal overflow at three breakpoints, and every rendered font
size is on the 8-step scale. Every one of those is a defect this repo has
actually shipped.

## The build

`python3 src/build.py` inlines `src/mod-*.js` into `src/sporve-web.host.html`
and writes `index.html`. **Edit the sources, never `index.html`.** Fonts and
hero images are base64'd in, because the built page must survive a CSP that
blocks every external request. `mod-companies.js` still fetches
`picsum.photos` externally, which violates that and is the one open warning in
the smoke test.
