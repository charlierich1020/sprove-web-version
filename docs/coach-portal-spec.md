# Coach-portal feature spec (for the real build)

Source: the 2026-08-09 brutal audit of the coach portal in the current sim. This is
the **NEEDS-BACKEND** half — what each surface must do to be best-in-class, and the
backend it requires. It is the feature spec for the Next.js + Supabase/AWS build, NOT
work to bolt onto the throwaway `index.html` (migration-brief directive 1).

Ordering follows the migration brief's **revenue-path** rule (Phase 4): the surfaces
a coach must have to get paid come first; delight surfaces come last.

Legend: **BE** = backend primitive it needs. **Bench** = best-in-class comparator.

---

## 0. What the sim already gets right (keep these invariants)

- Coach-finder **verified-only gate is real** — will not surface an unchecked coach
  (mirrors the prod `ai-match` structural filter). Preserve as a filter *before* any
  model, never a prompt request.
- Fee is a **single flat 12%** source. Keep one source of truth (DB-held config),
  never a client hardcode.
- Metrics are **Demo-labeled**. In prod, every number must be real or carry the pill.

---

## 1. Booking + payouts (revenue path — build first)

**Bench:** Stripe Dashboard / QuickBooks. **BE:** Stripe Connect, `bookings`/
`payouts` tables, webhook ledger, RLS.
- Real payout schedule + status (pending → in-transit → paid) from Stripe events, not
  a mock timeline.
- Itemization every coach can reconcile: gross, flat-12% fee, net — and it must equal
  what Stripe actually withheld (close gap #17: `platform_fee.dart` still projects
  18/4; the charged fee should be mirrored onto the booking row at webhook time and
  displayed from there).
- 1099-K projection from real annual totals; CSV export of real rows.
- Refunds compute from the cancellation policy **snapshotted at purchase** (server-side).
- Dispute/chargeback surface (read-only from Stripe).

## 2. Scheduling + capacity (revenue path)

**Bench:** Calendly / Acuity. **BE:** `availability`/`sessions` tables, capacity
trigger, RLS.
- Recurring availability; families book only real open slots.
- Seat capacity enforced at the **database** (advisory-locked trigger,
  `trg_enforce_booking_session_capacity`), never client-side — double-booking
  impossible.
- Conflict/blackout handling; timezone correct (Chicagoland = Central).

## 3. Roster / client records (revenue path)

**Bench:** a real CRM. **BE:** `athletes`/`consents` tables, RLS.
- One record per athlete: bookings history, session notes, consent status, media
  permission — all account-scoped by `auth.uid()`.
- No-consent-no-athlete invariant enforced server-side (consent row required before
  an athlete row exists, stamped version + timestamp).

## 4. Session notes (retention surface)

**Bench:** Google Docs / Notion. **BE:** `notes` table, realtime, storage.
- **Persistence + autosave** (the sim has neither) — a note survives reload.
- **Version history** — who changed what, restpoint.
- Rich text + templates (session plan, progress note, incident report).
- **Share with permissions** — parent sees the shared note; media in a note obeys the
  per-athlete media-consent tier (`none`/`private_share`/`public_profile`).
- Search across notes. (Real-time multi-editor collab is a stretch goal, not v1.)

## 5. Messaging / inbox (retention surface)

**Bench:** Slack / Intercom. **BE:** `messages` table, realtime channels, storage,
push.
- **Real delivery + persistence** (sim has UI only): a sent message reaches the other
  party and survives reload.
- Threads, read state, typing/presence from realtime, attachments (consent-gated),
  search, notifications (push/email fallback).
- Deferred-intent auth on first message (guest → auth → resume), per the sim's best
  decision.

## 6. Coach ops AI (the $20B differentiator — build after the money path works)

**Bench:** Linear/Notion AI, Intercom Fin. **BE:** `ai-gateway` (Anthropic-only,
service-role-gated), tool-calls over roster/calendar/booking, embeddings.
- **Grounded, tool-using assistant** — reads real roster/calendar/booking rows and
  *acts*: drafts the parent update, summarizes a session note, proposes a reschedule
  against live availability, flags an at-risk client from attendance/payment trends.
- Grounding = a **structural filter before the model** (unverified coaches excluded
  in code, never by prompt) — mirror `ai-match`.
- Honest UX: the command bar is an **assistant**, not a model marketplace. One
  identity ("Sporve AI"); if multiple models are ever offered, each must actually
  route (cost/latency/output differ) — otherwise it's one model.
- Every action the activity log claims must have actually happened (the sim's log
  overstated tab-switches as "Confirmed…"; in prod a log line is an audit artifact).

## 7. Insights (delight surface — last)

**Bench:** Amplitude / a real analytics dashboard. **BE:** aggregates over
`bookings`/`attendance`/`payments`.
- Real, actionable metrics (occupancy, retention, revenue trend, no-show rate) with
  cohorts/trends and period comparison — not vanity numbers.
- Every figure traceable to real rows; no fabricated deltas.

## 8. Media + consent (cross-cutting, safety)

**Bench:** a real consent system. **BE:** S3/Storage + per-athlete consent tier
enforced by storage/RLS policy.
- Per-athlete tier (`none`/`private_share`/`public_profile`); a coach can **request**,
  never grant. Enforcement is server-side at every publish/share action.

---

## Build order (revenue-path, per migration brief Phase 4)

1 → 2 → 3 (get a coach paid) · 4 → 5 (retain) · 6 (differentiate) · 7 → 8 (deepen).
The one finish line: one real Chicagoland coach onboarded, verified, booked, paid at
12%, refundable under a snapshotted policy — every claim true.
