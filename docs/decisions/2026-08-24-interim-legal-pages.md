# Interim legal pages — written in-house, dated for replacement

**Date:** 2026-08-24
**Status:** Accepted, temporary
**Replace by:** **2026-11-24** (90 days)

## Decision

Publish `/privacy`, `/terms`, `/refunds` and `/subprocessors` as standalone,
script-free pages written in-house, so that Stripe onboarding, A2P 10DLC carrier
review and app-store review have public URLs to read.

These are a **stopgap**, not counsel-reviewed policy. They are accurate about
what the product actually does — which most generator output is not — but they
have not been reviewed by a lawyer, and a youth-sports marketplace handling
children's data carries obligations (COPPA, state minor-privacy statutes,
Illinois BIPA if biometrics ever enter, background-check disclosure rules) that
no template addresses.

## Why standalone files rather than SPA routes

The legal text already existed inside the app as client-rendered views
(`info:privacy`, `info:terms`, `info:refund`). Those are invisible to the
audience that matters here: Stripe, carriers and app stores fetch these URLs
with a plain HTTP client that runs no JavaScript. Before this change,
`/privacy` returned **404** on every deployment.

`build.py` now emits four files from `src/legal/*.html`, and `cleanUrls` in
`vercel.json` serves `privacy.html` at `/privacy`. The pages carry no `<script>`
at all, so they add nothing to the CSP hash set.

## What must happen before the replace-by date

1. **Counsel review** of all four, specifically the children's-data handling,
   the background-check disclaimer in §4 of the Terms, and the liability
   limitation in §9.
2. **Reconcile the duplicate copy.** The SPA still renders its own older text
   from the `INFO` object. Two sources of legal truth is a defect; the
   standalone pages should become the only source and the SPA should link out
   to them.
3. **Confirm the entity string.** These pages say *Sporv Inc., Chicago, IL*.
   That must match the IRS CP 575 exactly before Stripe or A2P submission —
   see the entity/IRS match blocker.
4. **Re-check the subprocessor table.** Twilio is listed as *contracted, not yet
   integrated* and Resend and OpenAI as *provisioned, not enabled*, which is
   true on 2026-08-24. If any of them starts carrying live data, the table must
   change on the same day.

## Consequences if the date passes unactioned

The pages keep serving and keep being accurate about behaviour, so nothing
breaks operationally. The exposure is legal, not technical: unreviewed terms
limiting liability for sessions involving children is where that exposure is
concentrated.
