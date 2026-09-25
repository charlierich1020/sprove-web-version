# Incident — auto-executing implant in .vscode (folderOpen RCE)

**Detected / removed:** 2026-09-12
**Removal commits:** `8592531`, `30b5446` (CI tripwire), `f1b4baa` (second relocation)
**Evidence archive:** `incident-evidence-20260912-173502` — held outside every repo
**Status:** payload removed from HEAD; **still reachable in git history** (see Residual risk)

> Sections marked **[OWNER]** need facts only the owner has. They are left as
> explicit gaps rather than guesses, because an incident record that reads as
> complete while containing invention is worse than one that says what is unknown.

## What ran

A VS Code task on `main`, labelled `eslint-check` and hidden
(`hide:true`, `reveal:never`, `close:true`), with `runOptions.runOn: folderOpen`.
Opening the repository folder in VS Code silently executed:

```
node ./public/fonts/fa-solid-400.woff2
```

That file was not a font. **32,218 bytes** of space-padded, self-executing
obfuscated JavaScript — leading bytes `20 20 20 20…` (spaces), not `wOF2`.

```
sha256  9e286f7a54f071e5a4e9f09de84abca872d8347cbb7059c966c7db54a7e4dcba
blob    1390124885046fd4b6f6dd3a61410a8ae3cf9856
```

**Hash independently confirmed 2026-09-19** by extracting the blob from git and
hashing it, rather than by trusting the removal commit's own claim. They match.

Reported behaviour of the payload: spawns `child_process` with `windowsHide`,
reads command-and-control instructions from Ethereum RPC endpoints, fetches a
second stage over HTTPS. The C2-over-public-blockchain pattern is what makes the
channel hard to take down: there is no domain to sinkhole.

A second form appeared later — a non-standard `tasks` key inside
`settings.json` with the same `runOn: folderOpen` shape, plus
`"task.allowAutomaticTasks": true` — removed in `f1b4baa`.

## Exposure window

**[OWNER]** The window between the implant landing on `main` and its removal on
2026-09-12 was never reconstructed. Establishing it needs the commit that
introduced it, which is knowable from git, and an answer to which machines
opened the folder in VS Code during that period, which is not.

**[OWNER]** What the payload reached — credentials present on the developer
machine, whether the second stage was fetched, whether anything was exfiltrated.

## What was rotated

**[OWNER]** Record what was rotated and when: Supabase keys, Stripe keys,
Anthropic key, GitHub tokens, SSH keys, GPG keys, 2FA re-enrolment.

Known from the repo, not from rotation records: `GOLDEN_PW` was a literal in
`scripts/agent-golden.mjs` and remains readable in public history at `06db7d6`.
Its hardcoded fallback was removed 2026-09-24 so that rotation cannot be undone
by the next run. **Rotation of that account is [OWNER] and separate.**

## What was deliberately not reconstructed, and why

**[OWNER]** Your own launch checklist says to record this. Suggested framing:
full forensic reconstruction of a developer laptop was judged
disproportionate against wiping it and rotating everything, given no evidence of
lateral movement and no customer-data store on the machine. If that is the
reasoning, write it down — the value of this file is that the decision was made
knowingly rather than by omission.

## Controls added

- `scripts/no-implant-check.mjs` — CI tripwire failing the build on the payload
  hash, on either implant shape, and on any disguised binary.
- `.vscode/settings.json` sets `"task.allowAutomaticTasks": "off"`.
- The surviving `folderOpen` task is benign (`python3 -m http.server 8421`) and
  is disabled by the setting above regardless.

## Residual risk

**The payload is still reachable from `origin/main`'s history.** Re-verified
2026-09-24, twelve days after removal: the blob is still fetched by a normal
clone. It is inert as a git object, but `git checkout` of any commit before
`8592531` restores both the payload **and** the malicious `tasks.json` — the
version with `allowAutomaticTasks: true`. The hardening only exists in the
current commit; checking out an older one removes it.

**Until history is rewritten:** do not check out commits older than `8592531`,
and if you must, do it with VS Code closed. Purging needs `git filter-repo` and
a force-push affecting every clone, which is a decision about a shared public
repository, not a cleanup.

**Machines:** the Windows workstation used on 2026-09-24 was checked — the
payload has never been present in any working tree there, and no clone carries
the malicious `.vscode` task. Both `sporve-web-latest` and `sporve-web-srikanth`
hold the blob in `.git/objects` from ordinary fetches. `sprove-web-version` does
not.
