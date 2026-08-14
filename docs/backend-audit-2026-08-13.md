# Backend audit — 2026-08-13

Read-only probe of the live Supabase project (`tseszaprvtvqrkfpditu`) as an
anonymous client, using the publishable key already shipped in `mod-api.js`.
No rows were created: every write probe used an impossible foreign key, so the
statement could not succeed even where permission allowed it.

---

## 1. `bookings` accepts anonymous INSERT; only triggers stop it

**This is the finding that matters.**

`SELECT` is correctly locked down. Probed as an anonymous visitor:

| Table | Anonymous read |
| --- | --- |
| `providers` | `42501` permission denied |
| `athletes`, `bookings`, `profiles`, `messages` | `[]` — RLS filtered |
| `programs`, `sessions` | readable — public marketplace data, no PII |

`sessions` was inspected column by column (id, program_id, title, dates, times,
timezone, capacity, assigned_member_id). No personal data.

`INSERT` is a different story:

| Table | Anonymous insert |
| --- | --- |
| `programs` | `42501` — denied by RLS |
| `sessions` | `42501` — denied by RLS |
| **`bookings`** | **`P0001` — a trigger raised it, so RLS let the statement through** |

`P0001` is a PL/pgSQL `raise_exception`. Reaching it means the row passed the
row-level security check and was rejected later, by application logic:

```
session 00000000-0000-0000-0000-000000000000 does not resolve to a program
```

That is a data-integrity guard, not an authorisation one. It fired because the
identifiers were fake. **What it does not tell us is what happens when they are
real** — and `bookings` is the money table.

### Why this matters

The booking design is otherwise excellent: the client sends identifiers and
never a price, and `trg_set_booking_price` computes the amount server-side, so a
hostile client cannot buy a $120 session for $1. That defence is sound.

But price integrity is not the same as identity. The open question is whether
anything binds `searcher_id` to the caller. If no policy or trigger asserts
`auth.uid() = searcher_id`, an anonymous caller who supplies real ids could
create a booking attributed to somebody else. The twelve triggers enforce
consent, provider verification, capacity and the policy snapshot — all of which
are about the *booking*, not about *who is asking*.

Probing further would have risked creating a real booking in production, so it
was stopped here deliberately.

### What to check (dashboard, 2 minutes)

Supabase → **Authentication → Policies → `bookings`**. Confirm an `INSERT`
policy exists and that its `WITH CHECK` ties the row to the caller. If the only
policies are `SELECT`, or an INSERT policy exists with `WITH CHECK (true)`, this
is open.

### The fix, if it is missing

```sql
-- Anonymous callers must not be able to insert bookings at all.
revoke insert on public.bookings from anon;

-- An authenticated caller may only create bookings attributed to themselves.
create policy bookings_insert_own
  on public.bookings
  for insert
  to authenticated
  with check ( auth.uid() = searcher_id );
```

Then re-run the probe in this document: `bookings` should return `42501`, the
same as `programs` and `sessions`.

Belt and braces, since triggers already do the heavy lifting here — have the
booking trigger raise if `auth.uid() is distinct from new.searcher_id`, so the
guarantee survives a future policy edit.

---

## 2. Edge Function source is not in version control

Two functions are deployed and answering:

| Function | Probe result |
| --- | --- |
| `ai-gateway` | `401` — deployed, requires auth |
| `stripe-webhook` | `400` — deployed, rejected an unsigned request |
| `book-session`, `create-checkout`, `send-email` | `404` — not deployed |

`stripe-webhook` returning `400` rather than `404` is the point: **it exists.**
`mod-booking.js` also calls a `stripe-create-checkout` function that owns the
amount and the fee split.

There is no `supabase/` directory in this repository. That code — the code that
moves money — lives only in the dashboard. It cannot be reviewed in a PR, has no
history, cannot be rolled back, and disappears with the account.

### Pulling it in

Requires a Supabase personal access token, so it is the owner's to run:

```bash
# 1. Authenticate (opens a browser, or set SUPABASE_ACCESS_TOKEN)
npx supabase login

# 2. Link this repo to the project
npx supabase link --project-ref tseszaprvtvqrkfpditu

# 3. Download every deployed function into supabase/functions/
npx supabase functions download ai-gateway
npx supabase functions download stripe-webhook

# 4. Review before committing — check for hardcoded keys first
git add supabase/ && git commit -m "chore(supabase): vendor the deployed Edge Functions"
```

`supabase/.gitignore` in this directory already excludes local artifacts
(`.branches`, `.temp`, `.env`) so only source is committed.

### Read the webhook first

Before committing, confirm `stripe-webhook` verifies the Stripe signature with
`stripe.webhooks.constructEvent(body, sig, secret)` against the **raw** body. A
webhook that trusts an unsigned POST lets anyone mark a booking paid. The `400`
it returned to an unsigned request is consistent with correct verification, but
consistent is not the same as confirmed — the source will say.

---

## Still open from the previous audit

- **`/api/ai` accepts requests with no `Origin`/`Referer` on production.** Fixed
  in this repo (`api/ai.js`, `api/ai.origin.test.mjs`, 12/12 passing) but not on
  the deployment, which builds from `srikanthvishnu90-sketch/sporve-web`. A bare
  `curl` still gets a paid model completion.
- **No WAF rate limit** on `/api/ai`. The in-memory limiter resets on cold start
  and is per-instance, so it is not a quota.
