# Comprehension gaps — Sporve

Things the owner has not yet closed out. Seeded from an analysis of 170 of his
own messages across four repos over seven days, plus findings from a
seven-subsystem audit. Claude Code references this file and weaves these
topics into debrief questions.

**How to use it:** when you can answer the question in a sentence without
looking, delete the row. When a debrief exposes a new gap, add one.

---

## Tier 1 — you must understand these deeply

These are where a silent bug costs money, safety, or the company.

| # | Gap | The question that closes it |
|---|---|---|
| 1 | **Repo vs production drift.** 29 migrations say `AUTHORED, NOT YET APPLIED`; `reconcile/01_forward_schema.sql` says prod is a 36-table model missing ~30 tables created by migrations carrying no marker. Nothing in the audit is trustworthy until this is resolved. | Which migrations are actually applied to the production Supabase project right now? (`supabase migration list`) |
| 2 | **The platform fee is charged at a different rate than it is displayed.** DB seeds 1800bps first / 400bps recurring; `resolve_platform_fee_bps()` is never called from any edge function; the charge is a flat `PLATFORM_FEE_BPS ?? 1000` = 10%. The coach's finances screen mirrors 18/4. | On a first booking of $100, what does Stripe deduct, what does the coach see as net, and which is correct? |
| 3 | **RLS is the only thing between one parent and another parent's child.** One `USING (true)` policy exists (`availability_select_public`) — any logged-in user can read every coach's schedule. Its gated replacement is in the not-applied set. | Which tables can a signed-in parent read that belong to someone else? |
| 4 | **Google signup cannot create a coach.** Role goes as an OAuth query param; GoTrue drops it; `handle_new_user` falls to `'searcher'`. Unrecoverable because `prevent_profile_role_change` has no service-role exemption. | If a coach signed up with Google yesterday, what is their role and how would you fix it? |
| 5 | **Capacity is enforced nowhere on the live booking rail.** `enforce_booking_slot_capacity` no-ops when `service_id is null`, which is every booking `addBooking` creates. `enrolled_count` is never incremented. | What stops a session with 12 seats from taking a 13th booking? |

## Tier 2 — understand the shape

| # | Gap | The question that closes it |
|---|---|---|
| 6 | **Two matching engines disagree.** SQL `ltad_max_tier` is 0-4; Dart `_ceilingForAge` is 1-3, reading the same `intensity_tier` column. A 10-year-old gets different results in search vs chat. | Which code path decides what a 10-year-old is allowed to see, and does the other agree? |
| 7 | **The "only background-checked coaches" claim is enforced in one path and asserted in the other.** `ai-match` structurally cannot surface an unverified coach; `ai-chat` is a prompt asking the model not to. | Which AI surface could name an unverified coach, and what would stop it? |
| 8 | **Nothing resets on sign-out.** 23 of 24 root providers keep the previous account's roster, finances, children and chat in memory. | On a shared iPad, what does the second person to sign in see? |

## Tier 3 — open decisions, not knowledge gaps

Raised repeatedly across sessions and never resolved. Each needs a sentence,
not a study session.

| # | Open loop | The forcing question |
|---|---|---|
| 9 | Stack identity of `the-sporve-web` | Static `build.py` site or Next.js — which, this month? |
| 10 | Which URL is production | `sporve.vercel.app`, `the-sporve-web.vercel.app`, or `sporve-landing` — which one, and what are the others now? |
| 11 | Session partition | Which directories does the image session own exclusively? |
| 12 | Waitlist deliverability | Has a signup from a fresh address delivered an email in the last 24h — yes or no? |
| 13 | Demo dataset | Ten companies × five listings — final? |
| 14 | Type scale | Is 64px wanted? It is the one step in the requested scale that does not exist here. |

---

## Closed

**2026-08-06 — the five open decisions, answered by the owner.**

| was | answer | what it changes |
|---|---|---|
| 10. Which URL is production | **`the-sporve-web.vercel.app`.** | Confirms what has been deployed to all session. The other two are not production; nothing should be pushed to them without a decision. |
| 9. Stack identity | **Moving to Next.js.** | The largest open decision in the repo, now settled in direction. See the note below — it is a migration, not a switch, and nothing about it is started. |
| 11. Session partition | **Image session owns imagery across the board**, scoped to whichever site is actively being worked on. | Resolves the collision hazard from HANDOFF.md. Imagery = `assets/`. This session stays out of it. |
| 12. Waitlist deliverability | **No email has sent.** | Open BUG, not a gap. Moved to Tier 1 below. |
| 14. Type scale / 64px | **Do not change it arbitrarily — derive the size from evidence.** | Answered by measurement; see `docs/type-evidence.md`. Verdict: keep 52px. |

### A correction worth stating plainly

Next.js was described as "a type of JavaScript notation/language". It is
neither. JavaScript is the language. **React** is a library for building
interfaces in it, and **Next.js is a framework built on React** that adds
routing, server rendering and a build pipeline. TypeScript is the thing that
is "JavaScript with notation" — a superset that adds type annotations.

This matters practically, not pedantically: the cost of the migration is
almost entirely *React*, not Next.js. Moving to Next.js means rewriting every
one of these template-literal view functions as React components with state
and props. Next.js on top of that is mostly configuration.

---

## Tier 1 additions

| # | Gap | The question that closes it |
|---|---|---|
| 15 | **The waitlist has never delivered an email.** Confirmed by the owner. A signup form that silently drops the signup is worse than no form — the visitor believes they are on the list. | Where does a waitlist submission go, and what is the last hop that succeeds? |
