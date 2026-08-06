#!/usr/bin/env bash
# Smoke test for the-sporve-web.
#
# Why this exists: the repo had no test suite, no CI and no runner, so any
# automated change had nothing to verify itself against. Everything below is a
# check that a real defect in this repo has already tripped at least once:
#
#   boots        a ${...} pasted into a plain function body is a syntax error
#                that kills the whole host script -- shipped twice
#   errors       sportMenuHTML() was called and never defined; clicking the
#                first chip on the default route crashed the app, live
#   contrast     white-on-white headline (c6cf658), then near-black-on-black
#                under a dark theme -- both were INHERITED grounds, which a
#                CSS grep cannot see, so this resolves the painted background
#   overflow     new landing components broke the phone layout more than once
#   scale        the 8-step type scale drifts the moment someone hand-writes a px
#
# Exit 0 = safe to commit. Non-zero = revert, do not push.
# Usage: bash src/smoke.sh

set -uo pipefail
cd "$(dirname "$0")/.." || exit 2

B="$HOME/.claude/skills/gstack/browse/dist/browse"
FAIL=0
pass(){ printf "  \033[32mPASS\033[0m  %s\n" "$1"; }
fail(){ printf "  \033[31mFAIL\033[0m  %s\n" "$1"; FAIL=1; }

echo "── build ────────────────────────────────────────────"
if python3 src/build.py >/tmp/smoke-build.txt 2>&1; then
  pass "build.py exits 0"
else
  fail "build.py failed:"; sed 's/^/        /' /tmp/smoke-build.txt; exit 1
fi
grep -q "NONE FOUND" /tmp/smoke-build.txt && fail "fonts missing -- type contract not met" \
  || pass "all faces inlined"
[ -s index.html ] && pass "index.html emitted ($(wc -c < index.html) bytes)" \
  || { fail "index.html empty or missing"; exit 1; }

if [ ! -x "$B" ]; then
  echo "  browse not built -- runtime checks skipped (build checks passed)"
  exit $FAIL
fi

echo "── runtime ──────────────────────────────────────────"
$B viewport 1440x900 >/dev/null 2>&1
$B goto "file://$(pwd)/index.html" >/dev/null 2>&1

boots=$($B js "typeof S==='object'&&typeof render==='function'" 2>/dev/null | tr -d '[:space:]')
[ "$boots" = "true" ] && pass "host script boots" || { fail "host script did not boot"; exit 1; }

# Every route a visitor can reach without auth.
ROUTES="home explore product trust companies pricing coachinfo map assistant saved bookings messages timeline"
# A JS error is a code defect and fails the build. A failed external resource
# is an architecture problem (this page is meant to survive a CSP that blocks
# every external request) but it is pre-existing and environmental, so it warns
# rather than blocking a change that did not cause it.
RESWARN=0
for r in $ROUTES; do
  $B console --clear >/dev/null 2>&1
  $B js "S.auth={status:'guest'};S.portal='family';S.route={name:'$r',arg:null};render();'ok'" >/dev/null 2>&1
  log=$($B console --errors 2>&1)
  js=$(printf '%s' "$log" | grep "\[error\]" | grep -vc "Failed to load resource")
  res=$(printf '%s' "$log" | grep -c "Failed to load resource")
  [ "$js" -eq 0 ] || fail "JS errors on route '$r' ($js)"
  [ "$res" -eq 0 ] || { printf "  \033[33mWARN\033[0m  %s\n" "route '$r': $res external resource(s) failed to load"; RESWARN=$((RESWARN+res)); }
done
[ "$FAIL" -eq 0 ] && pass "no JS errors across $(echo $ROUTES | wc -w | tr -d ' ') routes"
[ "$RESWARN" -gt 0 ] && printf "  \033[33mWARN\033[0m  %s\n" "$RESWARN external image request(s) — see picsum.photos in mod-companies.js; the single-file/CSP design says nothing should be fetched externally"

# The dark-ground invariant. Resolves the PAINTED background through
# transparent ancestors -- both historic contrast failures were inherited.
bad=$($B js "
(()=>{const lum=c=>{const v=c.map(x=>{x/=255;return x<=.03928?x/12.92:Math.pow((x+.055)/1.055,2.4)});return .2126*v[0]+.7152*v[1]+.0722*v[2]};
const rgb=s=>{const m=s.match(/[\d.]+/g);return m?m.slice(0,3).map(Number):null};
const al=s=>{const m=s.match(/[\d.]+/g);return m&&m.length>3?Number(m[3]):1};
const bgOf=e=>{while(e){const c=getComputedStyle(e).backgroundColor;if(c&&al(c)>.5)return rgb(c);e=e.parentElement}return [255,255,255]};
const out=[];'$ROUTES'.split(' ').forEach(r=>{S.auth={status:'guest'};S.route={name:r,arg:null};render();
 document.querySelectorAll('body *').forEach(el=>{if(!el.offsetParent)return;
  if(![...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))return;
  const bg=bgOf(el);if(lum(bg)>.18)return;const fg=rgb(getComputedStyle(el).color);if(!fg)return;
  const q=(Math.max(lum(fg),lum(bg))+.05)/(Math.min(lum(fg),lum(bg))+.05);
  if(q<4.5)out.push(r+':'+(el.className||el.tagName)+'@'+q.toFixed(2))})});
return out.length?[...new Set(out)].slice(0,6).join(' | '):'CLEAN'})()" 2>/dev/null)
[ "${bad//\"/}" = "CLEAN" ] && pass "dark grounds carry white or slate text" \
  || fail "dark-ground violations: $bad"

# Layout must never scroll horizontally.
for vp in 1440x900 768x1024 390x844; do
  $B viewport "$vp" >/dev/null 2>&1
  $B goto "file://$(pwd)/index.html" >/dev/null 2>&1
  o=$($B js "S.route={name:'home',arg:null};render();document.body.scrollWidth>document.body.clientWidth" 2>/dev/null | tr -d '[:space:]')
  [ "$o" = "false" ] && pass "no horizontal overflow at $vp" || fail "horizontal overflow at $vp"
done

# Type scale. 21/22px are the documented unboxed-glyph exceptions.
off=$($B js "
(()=>{const ok=[10.5,12,13,14.5,15.5,21,22];const bad=new Set();
document.querySelectorAll('body *').forEach(el=>{if(!el.offsetParent)return;
 if(![...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))return;
 const s=parseFloat(getComputedStyle(el).fontSize);
 if(ok.includes(s))return;
 if(s>16&&s<20)return;      // --text-lg clamp
 if(s>=21&&s<=27)return;    // --text-xl clamp
 if(s>=24&&s<=32)return;    // --text-2xl clamp
 if(s>=32&&s<=54)return;    // --text-hero clamp
 bad.add(s)});
return bad.size?[...bad].join(','):'CLEAN'})()" 2>/dev/null)
[ "${off//\"/}" = "CLEAN" ] && pass "every rendered size is on the 8-step scale" \
  || fail "off-scale font sizes: $off"

echo "─────────────────────────────────────────────────────"
[ "$FAIL" -eq 0 ] && echo "  SMOKE PASSED" || echo "  SMOKE FAILED -- revert, do not push"
exit $FAIL
