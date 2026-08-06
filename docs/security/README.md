# Security testing — Sporve

## What runs

`clo` MODE: pentest, scheduled every 2 hours, against the real attack surface:
**`~/SportsMan-main` + Supabase** — 81 SQL migrations, 31 edge functions, the
RLS layer, Stripe webhooks, the ai-gateway. NOT `the-sporve-web`, which is one
static HTML file with no server, no database and no user input — a scanner
finds nothing there.

The methodology is distilled from Strix (usestrix/strix, the open-source AI
pentester, Apache 2.0), specifically its Supabase skill: mis-scoped RLS,
`service_role` exposure, edge functions trusting headers, unsafe RPCs. The
checklist lives in `.claude/agents/clo.md` under MODE: pentest.

## What it will and will not do

- **Reports every finding.** Ranked by blast radius × likelihood, with file:line
  and a concrete exploit. Latest run: `pentest-latest.md`. New vulnerabilities
  are appended to `docs/gaps.md` in the matching tier.
- **Never auto-patches a critical path.** RLS, Stripe, auth and migrations are
  findings-only — Clo drafts the fix and explains it; a human applies it. An
  unattended patch to a money or security surface is how a silent hole ships
  while nobody is watching. This is the one line that does not bend.
- **May PR non-critical fixes** on a branch, never merged.

## Two honest limits

1. **The schedule is session-scoped.** The cron lives in the Claude Code
   session that created it and dies when that session exits (and auto-expires
   after 7 days regardless). For a true always-on 2-hourly scan, it needs to be
   a GitHub Action or a system cron on a machine that stays up — a one-time
   setup, not something a chat session can guarantee.

2. **The full Strix runtime is not installed here.** Strix hard-requires Docker
   (not available in this environment) and Python 3.12+ (this machine has 3.9).
   When those are provisioned: `pipx install strix-agent`, set `LLM_API_KEY`,
   and run it as the deep dynamic pass. Until then, MODE: pentest is the static
   pass — which is where every backend finding to date has come from anyway.

## To run it now, by hand

Ask: *"Clo, MODE: pentest."*
