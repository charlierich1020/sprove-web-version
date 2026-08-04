#!/usr/bin/env python3
"""Inline every mod-*.js into the host HTML at the <!--MODULES--> marker.

Idempotent: always rebuilds from the pristine host (sporve-web.html), so
re-running after a new module lands simply re-inlines the full current set.
Outputs the built page to every distribution target.
"""
import glob, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOST = os.path.join(HERE, "sporve-web.html")
MARKER = "<!--MODULES-->"
TARGETS = [
    "/Users/vishnusrikanth/sporve-web/index.html",
    "/Users/vishnusrikanth/Downloads/sporve web/index.html",
    "/Users/vishnusrikanth/Downloads/sporve-web.html",
]
ORDER = [
    "mod-safety.js", "mod-reviews.js", "mod-coachops.js",
    "mod-payments.js", "mod-search.js", "mod-coachonboard.js",
    "mod-media.js", "mod-notes.js", "mod-insights.js",
]

host = open(HOST, encoding="utf-8").read()
if MARKER not in host:
    sys.exit("FATAL: %s marker missing from host" % MARKER)

found = {os.path.basename(p): p for p in glob.glob(os.path.join(HERE, "mod-*.js"))}
names = [n for n in ORDER if n in found] + sorted(n for n in found if n not in ORDER)

blocks, report = [], []
for n in names:
    src = open(found[n], encoding="utf-8").read()
    # A literal </script> inside a JS string would close the tag early.
    src = src.replace("</script>", "<\\/script>")
    blocks.append("<script>\n/* ---- %s ---- */\n%s\n</script>" % (n, src))
    report.append("  %-18s %6d bytes" % (n, len(src)))

built = host.replace(MARKER, "\n".join(blocks) if blocks else MARKER)

# The Artifact platform supplies <!doctype>/<head>, but a file opened from disk
# or served by a plain static server does not — without an explicit charset the
# browser falls back to latin-1 and every emoji/en-dash renders as mojibake.
# Local copies therefore get a complete standalone document.
STANDALONE = (
    '<!doctype html>\n<html lang="en">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
    '<meta name="description" content="Sporve for Web - every sport, one app.">\n'
    "</head>\n<body>\n%s\n</body>\n</html>\n"
)

for t in TARGETS:
    os.makedirs(os.path.dirname(t), exist_ok=True)
    with open(t, "w", encoding="utf-8") as f:
        f.write(STANDALONE % built)

print("inlined %d module(s):" % len(names))
print("\n".join(report) if report else "  (none yet)")
print("built size: %d bytes" % len(built))
print("targets:")
for t in TARGETS:
    print("  %s  %s" % ("OK " if os.path.exists(t) else "FAIL", t))
