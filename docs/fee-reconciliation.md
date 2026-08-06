# Fee reconciliation — flat 12%, every booking  [CRITICAL-PATH · DRAFT, NOT APPLIED]

**Decision (owner, 2026-08-06):** Sporve takes a **flat 12% of every booking.
No first-vs-recurring split. No off-platform SaaS rate. No other fees.**
`$80 booking → Sporve keeps $9.60 → coach nets $70.40.`

This supersedes the 18% / 4% / 2.5% "we charge for introductions, not
relationships" schedule that is currently written into the code. That schedule
was **never live** — the production Supabase project (`tseszaprvtvqrkfpditu`) is
applied only through migration `20260725033343`, and the `platform_fees` /
`resolve_platform_fee_bps` migration (`20260728_000101`) that would have seeded
18/4 is not among the applied set. So today's live charge is the flat env-var
default (10%), and the coach UI *projects* 18/4 — **both are wrong; canonical is
12%.**

Nothing below has been applied. This is the review artifact; apply on approval.

---

## 1 — Charge side · Stripe application fee  (repo: `~/SportsMan-main`)

The charge is already a single flat rate, so this is a value change, not a
rearchitecture — the 18/4 resolver is never called from checkout.

| Where | Today | Change to |
|---|---|---|
| `supabase/functions/stripe-create-checkout/index.ts:49` | `Number(Deno.env.get("PLATFORM_FEE_BPS") ?? 1000)` | `?? 1200` |
| same file, header comment `:9` | "keeps an application fee (PLATFORM_FEE_BPS, default 10%)" | "flat 12%" |
| Deployed edge-function secret `PLATFORM_FEE_BPS` | unknown live value — **must confirm** | set to `1200` |

The fee math (`Math.round(amount * bps / 10000)`, `:168`) and the `≤3000` bps
guard (`:161-163`) are correct for 1200 and need no change. **Action to confirm
the live value:** Supabase Dashboard → project `tseszaprvtvqrkfpditu` → Edge
Functions → Manage secrets → read/set `PLATFORM_FEE_BPS = 1200`. Until the
secret is set, the code default governs — so the default and the secret must
agree on 1200.

## 2 — Display side · coach-facing projection  (repo: `~/SportsMan-main`)

`lib/core/utils/platform_fee.dart` is the single source of truth for the
itemization the coach sees. It currently encodes the retired schedule:

```
kFirstBookingFeeBps  = 1800   // 18% first booking      → REMOVE
kRecurringFeeBps     = 400    // 4% thereafter          → REMOVE
kOffPlatformFeeBps   = 250    // 2.5% off-platform SaaS  → REMOVE
```

Collapse to one constant `kPlatformFeeBps = 1200` and drop the `isFirst` /
`isOffPlatform` branching (and the "SaaS fee" vs "platform fee" labels) so every
line itemizes at 12%. Downstream that touches: `commission_itemization_card.dart`
(the `Sporve fee (${item.platformRatePct})` row now always reads 12%),
`earnings_csv.dart`, `team_split.dart`, and the finances/payouts screens that
consume `FeeItemization`. These are display-only (the files declare
`MONEY HONESTY (L-003): moves NO money`), so they cannot mischarge — but a stale
number here misleads the coach about their net, which is the trust cost.

**Out of scope, flagged for your call:** `commission.dart` /
`commission_rates` is the *org↔trainer* split (an org's internal cut of its own
trainer's booking) — a different party's money, behind a design-only flag, not a
Sporve fee. "12% flat, no other fees" is about *Sporve's* rake; it does not
obviously delete the org/trainer feature. Confirm whether that stays.

## 3 — DB side · Supabase  (apply mode: DRAFT + REVIEW, per your choice)

- `20260728_000101_platform_fees.sql` (seeds 1800/400, defines
  `resolve_platform_fee_bps`) is now **obsolete** — do not apply; stage for
  removal from the repo so no future `db push` reintroduces the 18/4 model.
- No new migration is required for the 12% flat fee: the rate lives in the edge
  secret, not a table. A migration would only be needed if you later want the
  rate DB-driven.
- Independent hardening surfaced by `get_advisors(security)` on the live project,
  each staged for review (not applied): revoke `anon`/`authenticated` EXECUTE on
  the two `SECURITY DEFINER` funcs callable unauthenticated (`rls_auto_enable`,
  `is_org_admin`); the 11 `RLS-enabled-no-policy` tables (incl. `waitlist` —
  candidate cause of Tier-1 #15, signups never delivering); enable leaked-password
  protection (Auth settings toggle).

---

## Blast radius / order of operations

1. Set `PLATFORM_FEE_BPS=1200` secret **and** land the `?? 1200` default in the
   same change, so charge = 12% regardless of which governs.
2. Land the `platform_fee.dart` collapse so the coach preview reads 12% and
   matches the charge — do this in lockstep with (1) to avoid a window where
   charge (12%) and display (18/4) disagree again.
3. Retire migration `20260728_000101` from the repo.
4. Backfill: any booking already charged at 10% before the cutover carries the
   old rate on its Stripe record — decide whether to reconcile historically or
   apply 12% forward-only (recommend forward-only; Stripe fees are immutable
   post-charge).
