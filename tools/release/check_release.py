#!/usr/bin/env python3
"""Checks for the release build. Run before publishing.

  default   structure + content checks; tokens are listed, not failed
  --final   also fails on any %%TOKEN%% left, and checks every external link answers

Checks: tag balance on every page; every JSON-LD block parses; the four new lyrics
pages match tools/release/lyrics.json word for word (visible text AND schema text);
writers lines match the confirmed roster; no pre-release wording left on public
pages; every internal link and image points at a file that exists.
Run:  /usr/bin/python3 tools/release/check_release.py [--final]
"""
import html
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LYR = json.loads((ROOT / "tools/release/lyrics.json").read_text(encoding="utf-8"))
FINAL = "--final" in sys.argv
SKIP = ("tools/", "variants/", "artifact-preview/", ".git/")
ROSTER = {"tat-twam-asi": "Anya Gupta, Sarah Simmons, Greg Langston and Himani Gupta"}
DEFAULT_WRITERS = "Anya Gupta, Sarah Simmons and Greg Langston"
# wording that must not survive on public pages after release (privacy/ may explain pre-saves)
STALE = [r"arrives September", r"[Pp]re-save", r"days until", r"Visuals · Sep 18", r"out September 18",
         r"releases September 18", r"premiere alongside"]
fails, notes = [], []


class Balance(HTMLParser):
    VOID = {"meta", "link", "img", "br", "hr", "input", "source", "wbr", "path", "circle", "rect", "line", "polyline", "ellipse"}

    def __init__(self):
        super().__init__()
        self.stack, self.errs = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                self.errs.append(f"unclosed <{self.stack.pop()}>")
            self.stack.pop()
        else:
            self.errs.append(f"stray </{tag}>")


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT).as_posix()
        if not rel.startswith(SKIP):
            yield p, rel


def key(s):
    return re.sub(r"\s+", " ", html.unescape(s).replace("’", "'")).strip()


for p, rel in pages():
    s = p.read_text(encoding="utf-8")
    b = Balance()
    b.feed(s)
    errs = b.errs + [f"unclosed <{t}>" for t in b.stack if t not in ("html", "body", "head")]
    if errs:
        fails.append(f"{rel}: tags — {errs[:4]}")
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            json.loads(block)
        except Exception as e:
            fails.append(f"{rel}: JSON-LD does not parse — {e}")
    toks = sorted(set(re.findall(r"%%[A-Z_]+%%", s)))
    if toks:
        (fails if FINAL else notes).append(f"{rel}: tokens {toks}")
    if rel not in ("privacy/index.html",) and not rel.startswith("rsvp/"):
        visible = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", s, flags=re.S)
        for pat in STALE:
            for m in re.finditer(pat, visible):
                fails.append(f"{rel}: pre-release wording left: …{visible[max(0, m.start()-40):m.end()+30]!r}…")
    # internal links + images exist
    for attr in re.findall(r'(?:href|src)="([^"#?]+)', s):
        if attr.startswith(("http", "mailto:", "data:", "%%", "//")):
            continue
        target = (ROOT / attr.lstrip("/")) if attr.startswith("/") else (p.parent / attr)
        if target.is_dir() or attr.endswith("/"):
            target = target / "index.html"
        if not target.exists():
            fails.append(f"{rel}: broken internal link {attr}")
    # writers line
    m = re.search(r'<p class="writers-line">Written by (.*?)</p>', s)
    if m and rel.startswith("songs/"):
        slug = rel.split("/")[1]
        want = ROSTER.get(slug, DEFAULT_WRITERS)
        if m.group(1) != want:
            fails.append(f"{rel}: writers line {m.group(1)!r} != roster {want!r}")

# lyrics: visible and schema text must equal lyrics.json
for slug, d in LYR.items():
    s = (ROOT / f"songs/{slug}/index.html").read_text(encoding="utf-8")
    want = [[key(l) for l in st] for st in d["stanzas"]]
    block = re.search(r'<div class="lyrics">(.*?)</div>', s, re.S).group(1)
    got = [[key(re.sub(r"<[^>]+>", "", l)) for l in p_.split("<br>")]
           for p_ in re.findall(r"<p>(.*?)</p>", block, re.S)]
    if got != want:
        fails.append(f"songs/{slug}: visible lyrics differ from lyrics.json")
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S).group(1))
    text = ld["recordingOf"]["lyrics"]["text"]
    if [[key(l) for l in st.split("\n")] for st in text.split("\n\n")] != want:
        fails.append(f"songs/{slug}: schema lyrics differ from lyrics.json")
    if ld["name"] != d["title"]:
        fails.append(f"songs/{slug}: schema name {ld['name']!r} != {d['title']!r}")

if FINAL:
    ext = set()
    for p, rel in pages():
        ext |= set(re.findall(r'href="(https://(?:open\.spotify\.com|music\.apple\.com|distrokid\.com)[^"]+)"', p.read_text(encoding="utf-8")))
    for u in sorted(ext):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20)
            if r.status >= 400:
                fails.append(f"link {u} -> {r.status}")
        except Exception as e:
            fails.append(f"link {u} -> {type(e).__name__} {e}")

print("\n".join("· " + n for n in notes))
print("\n".join("✗ " + f for f in fails) if fails else "✓ all checks passed" + (" (final)" if FINAL else ""))
sys.exit(1 if fails else 0)
