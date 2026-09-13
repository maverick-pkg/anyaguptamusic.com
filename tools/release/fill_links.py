#!/usr/bin/env python3
"""Release night: put the real links into the site files, replacing %%TOKENS%%.

Refuses to change anything if any token used in the site has no value in
links.json, and fails afterwards if any %%TOKEN%% is left anywhere.
Run:  /usr/bin/python3 tools/release/fill_links.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINKS = json.loads(Path(__file__).with_name("links.json").read_text())
TOKEN = re.compile(r"%%([A-Z_]+)%%")
SKIP = ("tools/", "variants/", "artifact-preview/", ".git/")


def site_files():
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT).as_posix()
        if p.is_file() and p.suffix in (".html", ".xml") and not rel.startswith(SKIP):
            yield p, rel


def main():
    used = {}
    for p, rel in site_files():
        for t in TOKEN.findall(p.read_text(encoding="utf-8")):
            used.setdefault(t, set()).add(rel)
    missing = {t: sorted(f) for t, f in used.items() if not LINKS.get(t)}
    if missing:
        print("STOP — no value yet for:")
        for t, f in sorted(missing.items()):
            print(f"  {t:34} used in {', '.join(f)}")
        sys.exit(1)
    changed = 0
    for p, rel in site_files():
        s = p.read_text(encoding="utf-8")
        n = TOKEN.sub(lambda m: LINKS[m.group(1)], s)
        if n != s:
            p.write_text(n, encoding="utf-8")
            changed += 1
            print("  filled", rel)
    left = [rel for p, rel in site_files() if TOKEN.search(p.read_text(encoding="utf-8"))]
    if left:
        sys.exit(f"STOP — tokens still present in: {left}")
    print(f"done: {changed} file(s) filled, no tokens left")


if __name__ == "__main__":
    main()
