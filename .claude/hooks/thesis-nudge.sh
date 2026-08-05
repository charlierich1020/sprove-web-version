#!/usr/bin/env bash
# UserPromptSubmit hook — fires the thesis pass on pasted recommendations.
#
# Why length-gated rather than every prompt: a thesis pass on "yes" or "push
# that" is pure cost and noise. A pasted spec, brief or recommendation is long.
# 900 chars is comfortably above a normal instruction and below any real brief.
#
# The hook cannot invoke a subagent itself — hooks run shell, not the agent
# loop. What it can do is put an instruction into the turn's context, which is
# what this does. Claude then invokes the `thesis` agent before writing code.
#
# Remove by deleting the UserPromptSubmit block from .claude/settings.json.

payload=$(cat)
prompt=$(printf '%s' "$payload" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("prompt",""))' 2>/dev/null || echo "")
len=${#prompt}

[ "$len" -lt 900 ] && exit 0

cat <<'EOF'
<system-reminder>
The message above is long enough to be a pasted recommendation, spec, or brief.
Per the owner's standing instruction: run the `thesis` agent
(.claude/agents/thesis.md) on it BEFORE writing any code, and report its
thesis. If the message is not actually a recommendation — it is a long bug
report, a stack trace, or a direct instruction — skip the thesis pass and say
in one line that you skipped it and why.
</system-reminder>
EOF
