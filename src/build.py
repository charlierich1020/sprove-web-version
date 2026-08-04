#!/usr/bin/env python3
"""Inline every mod-*.js into the host HTML at the <!--MODULES--> marker.

Idempotent: always rebuilds from the pristine host (sporve-web.html), so
re-running after a new module lands simply re-inlines the full current set.
Outputs the built page to every distribution target.
"""
import glob, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOST = os.path.join(HERE, "sporve-web.host.html")
MARKER = "<!--MODULES-->"
TARGETS = [os.path.join(ROOT, "index.html")]
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

# The hero photograph is inlined as a data URI rather than linked: the page has
# to stay one self-contained file that survives a CSP blocking every external
# request. Drop any assets/hero-stadium.{jpg,jpeg,png,webp} in and it is picked
# up automatically; with none present the token stays and the CSS gradient
# fallback renders instead.
# Sentinel is a paid Hoefler&Co face and is deliberately NOT in this repo.
# Drop the licensed webfonts in assets/fonts/ and they get emitted as @font-face
# rules with the binaries inlined, so the single-file + CSP constraints hold.
# Filenames drive weight/style: Sentinel-Bold.woff2, Sentinel-BookItalic.woff2, ...
FONT_WEIGHTS = {"light": 300, "book": 400, "roman": 400, "regular": 400,
                "medium": 500, "semibold": 600, "bold": 700, "black": 800}
font_files = sorted(glob.glob(os.path.join(ROOT, "assets", "fonts", "*.woff2")))
faces = []
for fp in font_files:
    stem = os.path.basename(fp).rsplit(".", 1)[0]
    tail = stem.split("-", 1)[1].lower() if "-" in stem else "book"
    italic = "italic" in tail
    weight = next((v for k, v in FONT_WEIGHTS.items() if k in tail.replace("italic", "")), 400)
    import base64 as _b64
    with open(fp, "rb") as f:
        b64 = _b64.b64encode(f.read()).decode("ascii")
    faces.append(
        '@font-face{font-family:"Sentinel";font-weight:%d;font-style:%s;font-display:swap;'
        'src:url(data:font/woff2;base64,%s) format("woff2")}'
        % (weight, "italic" if italic else "normal", b64))
if faces:
    built = built.replace("/*__FONTFACE__*/", "\n".join(faces))
    print("fonts: %d Sentinel face(s) inlined" % len(faces))
else:
    print("fonts: none at assets/fonts/*.woff2 — falling back to Rockwell/slab stack")

HERO_TOKEN = "__HERO_IMG__"
hero_dir = os.path.join(ROOT, "assets")
hero = next((p for ext in ("jpg", "jpeg", "png", "webp")
             for p in glob.glob(os.path.join(hero_dir, "hero-stadium." + ext))), None)
if hero:
    import base64
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}[hero.rsplit(".", 1)[1].lower()]
    with open(hero, "rb") as f:
        raw = f.read()
    uri = "data:image/%s;base64,%s" % (mime, base64.b64encode(raw).decode("ascii"))
    built = built.replace('"%s".indexOf("__HERO") === 0 ? "" : "%s"' % (HERO_TOKEN, HERO_TOKEN),
                          '"%s"' % uri)
    print("hero image: %s (%.0f KB inlined)" % (os.path.basename(hero), len(raw) / 1024))
else:
    print("hero image: none at assets/hero-stadium.* — gradient fallback in use")

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
