# The Sporve Web

The web counterpart to the Sporve mobile app — a youth-sports marketplace connecting
families with background-checked coaches across 20+ sports.

Same product, same data, same functionality as the Flutter app; light theme and a
desktop layout. Airbnb's model: one product, two surfaces.

**Every sport. One app.**

---

## Run it

`index.html` is a single self-contained file. No build step, no install, no server.

```bash
open index.html
```

Or serve it:

```bash
python3 -m http.server 8420
# http://127.0.0.1:8420
```

The only network requests are to `picsum.photos` for placeholder photography —
the same placeholders the source app uses.

---

## Two sides

Switch with the **Family / Coach** toggle in the header.

**Family** — Explore (30 listings, 20+ sports), Map, AI Coach, Bookings, Schedule,
Messages, Saved, Profile, Athlete progress, Goals & plan, Notifications, Trust & safety.

**Coach** — Home dashboard, Schedule, Bookings, Clients, Messages, Services &
locations, Earnings, Reviews, Policies, Waitlist, Recurring slots, Automated
messages, Media, Session notes, Insights, Business profile.

---

## Data

Thirty listings across six businesses, transcribed verbatim from the source app's
`lib/core/mock/mock_data.dart`. Sport colors copied from `sport_colors.dart` —
OKLCH-calibrated, and the only chromatic layer in the design.

Nothing about the catalogue is invented. Two of the six businesses (Everglade
Racquet Institute, Sunset Field Athletics) show "Verification pending" instead of
the trust badge because their background checks have not cleared.

---

## What is actually enforced

These are not labels. They hold in the code:

- **Background checks are per person, never per business.** An approved
  organization never vouches for an individual on its roster. Unverified coaches
  are filtered out before sport, age, or budget in the AI matcher.
- **Parental consent gates child profiles.** No consent checkbox, no athlete
  record. Consent is stamped with a version and timestamp.
- **Media consent is enforced, not advisory.** Photos of minors carry a per-athlete
  flag (`none` / `private_share` / `public_profile`). A coach can request consent
  but can never grant it on a family's behalf.
- **Reviews unlock only after a completed session** — not merely a booking.
- **Refunds follow the cancellation policy snapshotted at purchase**, not whatever
  the listing says later.
- **Coaches cannot self-verify.** Verification, background-check, and payout fields
  are read-only on the coach's own profile.
- **Guests browse freely.** Auth is triggered by an action (book / message / save),
  never a wall — and the deferred action resumes itself after sign-in.

---

## Layout

```
index.html              the built app (single file)
src/
  sporve-web.host.html  host app with a <!--MODULES--> placeholder
  mod-safety.js         safety reports, refunds, privacy requests
  mod-reviews.js        reviews, athlete timeline, goals & plan
  mod-coachops.js       policies, waitlist, recurring slots, automated messages
  mod-payments.js       checkout, cancellation refunds, wallet, split pay
  mod-search.js         advanced filters, sort, saved searches, compare
  mod-coachonboard.js   7-step coach onboarding wizard
  mod-media.js          media library with per-athlete consent enforcement
  mod-notes.js          session notes and progress reports
  mod-insights.js       demand, funnel, price positioning, client watchlist
  build.py              inlines every module into index.html
```

Rebuild after editing anything in `src/`:

```bash
python3 src/build.py
```

Each module registers a `window.MOD_*` object exposing `{css, views, modals, tabs,
wire, state}`. The host discovers them at boot, merges their state, injects their
CSS, and routes to their views. Modules never touch the host file, so they can be
built independently and dropped in.

---

## Stack

Vanilla JavaScript. No framework, no bundler, no dependencies, no CDN.

The whole thing is one HTML file because it has to survive a strict CSP that blocks
every external request. Typography is Arial across both roles — it ships on every
OS, so nothing silently falls back to something you didn't choose.

---

## Contact

support@sporve.com · Miami, FL

Sporve is a marketplace connecting families with independent coaches.
