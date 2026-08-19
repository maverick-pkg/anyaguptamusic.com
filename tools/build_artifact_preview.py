#!/usr/bin/env python3
"""Build the claude.ai artifact preview fragment from the live homepage.
Output goes to the session scratchpad path bound to the artifact URL."""
import base64, os, re, subprocess, sys, urllib.request

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(SITE, "index.html")
ASSETS = os.path.join(SITE, "assets")
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/variant-d-artifact.html"
TMP = os.path.join(os.path.dirname(OUT), "artifact_imgs")
os.makedirs(TMP, exist_ok=True)

UA = "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
BIG = {"photos/hero-desktop.jpg", "photos/shows-band.jpg", "photos/contact-band.jpg", "photos/music-backdrop.jpg"}

def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30).read()

def embed_fonts(css2_url):
    css = fetch(css2_url).decode()
    out = []
    for subset, face in re.findall(r"/\*\s*(\w[\w-]*)\s*\*/\s*(@font-face\s*\{[^}]*\})", css):
        if subset != "latin":
            continue
        m = re.search(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", face)
        if m:
            b64 = base64.b64encode(fetch(m.group(1))).decode()
            out.append(face.replace(m.group(1), f"data:font/woff2;base64,{b64}"))
    if not out:
        sys.exit("no latin faces")
    return "<style>\n" + "\n".join(out) + "\n</style>"

def data_uri(rel):
    src = os.path.join(ASSETS, rel)
    if rel.endswith(".png"):
        return "data:image/png;base64," + base64.b64encode(open(src, "rb").read()).decode()
    cap = 520 if rel.startswith("covers/") else (1000 if rel in BIG else 700)
    small = os.path.join(TMP, rel.replace("/", "_"))
    subprocess.run(["sips", "-Z", str(cap), "-s", "format", "jpeg", "-s", "formatOptions", "70",
                    src, "--out", small], check=True, capture_output=True)
    return "data:image/jpeg;base64," + base64.b64encode(open(small, "rb").read()).decode()

html = open(SRC).read()
title = re.search(r"<title>.*?</title>", html, re.S).group(0)
css2 = re.search(r'href="(https://fonts\.googleapis\.com/css2[^"]+)"', html).group(1).replace("&amp;", "&")
head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
styles = "\n".join(re.findall(r"<style>.*?</style>", head, re.S))
body = re.search(r"<body>(.*?)</body>", html, re.S).group(1)
frag = "\n".join([title, '<meta name="viewport" content="width=device-width, initial-scale=1">',
                  embed_fonts(css2), styles, body])
for rel in sorted(set(re.findall(r'assets/([\w\-./]+\.(?:jpg|png))', frag))):
    frag = frag.replace(f"assets/{rel}", data_uri(rel))
if "fonts.googleapis" in frag or re.search(r"<(html|head|body)[\s>]", frag):
    sys.exit("shell or external refs remain")
open(OUT, "w").write(frag)
print(f"{os.path.basename(OUT)}: {len(frag)/1e6:.2f}MB")
