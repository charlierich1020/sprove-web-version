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

# (The hero photographs are handled further down, next to their token.)
# Sentinel is a paid Hoefler&Co face and is deliberately NOT in this repo.
# Drop the licensed webfonts in assets/fonts/ and they get emitted as @font-face
# rules with the binaries inlined, so the single-file + CSP constraints hold.
# Filenames drive weight/style: Sentinel-Bold.woff2, Sentinel-BookItalic.woff2, ...
# Order matters — the first key found in the tail wins, so "extrabold" has to be
# tested before "bold" or every ExtraBold file would inline as 700.
FONT_WEIGHTS = {"light": 300, "book": 400, "roman": 400, "regular": 400,
                "medium": 500, "semibold": 600, "extrabold": 800,
                "bold": 700, "black": 800}
# The filename PREFIX names the family, so every contracted face inlines from
# the same drop folder:
#   Syne-Variable.woff2    -> font-family:"Syne",              weight 600 800
#   Jakarta-Variable.woff2 -> font-family:"Plus Jakarta Sans",  weight 400 700
# Anything else keeps working under its own prefix (e.g. Sentinel-Book.woff2).
FAMILY_BY_PREFIX = {
    "syne": "Syne",
    "jakarta": "Plus Jakarta Sans",
    "bricolage": "Bricolage Grotesque",
    "hanken": "Hanken Grotesk",
    "sentinel": "Sentinel",
}
# Google serves ONE variable woff2 per family — every weight URL in a css2
# response for Syne or Plus Jakarta Sans returns a byte-identical file. Seven
# static faces would have been 208KB of duplicate binary; two variable faces are
# 60KB. A file named <Prefix>-Variable.woff2 therefore emits a single @font-face
# carrying the whole weight range instead of one face per weight.
VARIABLE_RANGE = {"Syne": "600 800", "Plus Jakarta Sans": "400 700"}
font_files = sorted(glob.glob(os.path.join(ROOT, "assets", "fonts", "*.woff2")))
faces, fam_seen = [], set()
for fp in font_files:
    stem = os.path.basename(fp).rsplit(".", 1)[0]
    prefix = stem.split("-", 1)[0].lower()
    family = FAMILY_BY_PREFIX.get(prefix, stem.split("-", 1)[0])
    tail = stem.split("-", 1)[1].lower() if "-" in stem else "regular"
    italic = "italic" in tail
    if "variable" in tail:
        weight = VARIABLE_RANGE.get(family, "100 900")
    else:
        weight = next((v for k, v in FONT_WEIGHTS.items() if k in tail.replace("italic", "")), 400)
    import base64 as _b64
    with open(fp, "rb") as f:
        b64 = _b64.b64encode(f.read()).decode("ascii")
    faces.append(
        '@font-face{font-family:"%s";font-weight:%s;font-style:%s;font-display:swap;'
        'src:url(data:font/woff2;base64,%s) format("woff2")}'
        % (family, weight, "italic" if italic else "normal", b64))
    fam_seen.add(family)
if faces:
    built = built.replace("/*__FONTFACE__*/", "\n".join(faces))
    print("fonts: %d face(s) inlined across %s" % (len(faces), ", ".join(sorted(fam_seen))))
else:
    print("fonts: NONE FOUND at assets/fonts/*.woff2")
    print("       The type contract names Syne (display) + Plus Jakarta Sans")
    print("       (body). Neither is present, so the page renders on the system")
    print("       fallback stacks and the contract is NOT met.")
    print("       Drop Syne-Variable.woff2 and Jakarta-Variable.woff2 into")
    print("       assets/fonts/ and rebuild. Both are OFL, from Google Fonts.")

# The hero photographs are inlined as data URIs rather than linked, for the same
# single-file/CSP reason as the fonts. Every assets/hero-*.{jpg,jpeg,png,webp} is
# picked up, sorted by filename — that sort IS the slideshow order, so the names
# carry it (hero-1-swimming.jpg, hero-2-tennis.jpg). With none present the token
# stays and the CSS gradient fallback renders instead.
HERO_TOKEN = "__HERO_IMGS__"
MIME = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}
hero_dir = os.path.join(ROOT, "assets")
heroes = sorted(p for ext in MIME for p in glob.glob(os.path.join(hero_dir, "hero-*." + ext)))
if heroes:
    import base64
    uris, hero_bytes = [], 0
    for h in heroes:
        with open(h, "rb") as f:
            raw = f.read()
        hero_bytes += len(raw)
        uris.append("data:image/%s;base64,%s"
                    % (MIME[h.rsplit(".", 1)[1].lower()], base64.b64encode(raw).decode("ascii")))
    built = built.replace('"%s".indexOf("__HERO") === 0 ? [] : []' % HERO_TOKEN,
                          "[%s]" % ",".join('"%s"' % u for u in uris))
    print("hero images: %d inlined (%.0f KB) — %s"
          % (len(heroes), hero_bytes / 1024, ", ".join(os.path.basename(h) for h in heroes)))
    if len(heroes) != 2:
        print("       NOTE: the @keyframes stops in the host are written against a")
        print("       TWO-photograph cycle. %d photographs will still cycle, but the"
              % len(heroes))
        print("       hold/slide split will be off — recompute them (see .hero-media).")
else:
    print("hero images: none at assets/hero-*.* — gradient fallback in use")

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
