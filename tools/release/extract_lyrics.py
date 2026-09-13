#!/usr/bin/env python3
"""Extract the lyrics of the four new Becoming songs into tools/release/lyrics.json.

Source of the WORDS: the official album lyrics PDF
  ~/Dropbox (Personal)/Music/Anya/Lyrics/Full Album Lyrics.pdf  (Aug 10 2026)
— the same text the family-approved lyric videos show.

Stanzas: read with `pdftotext -layout`, which keeps the blank line between verses
(plain mode drops them). A page break can fall in the middle of a verse, so at each
page break inside a song we look at the two lines on either side in the July
whole-album Word draft (~/Dropbox (Personal)/Music/Anya/Not for you/NotForYouLyrics.docx)
and keep a verse break there only if the draft has one. Everywhere else the PDF decides.
The report prints each song's verse shape next to the draft's, so a lost or invented
break shows up before anything is built.

Typography: straight apostrophes become ’ (words unchanged). Surrounding spaces go.
Run:  /usr/bin/python3 tools/release/extract_lyrics.py      (needs pdftotext + python-docx)
"""
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
PDF = HOME / "Dropbox (Personal)/Music/Anya/Lyrics/Full Album Lyrics.pdf"
DOCX = HOME / "Dropbox (Personal)/Music/Anya/Not for you/NotForYouLyrics.docx"
OUT = Path(__file__).with_name("lyrics.json")

SONGS = {  # canonical titles (must match DistroKid) -> slug, track number
    "Not For You": ("not-for-you", 2),
    "Let You Be": ("let-you-be", 4),
    "Breakup with My Ego": ("breakup-with-my-ego", 5),
    "Life Vest": ("life-vest", 7),
}
ALL_TITLES = ["You’re Original", "Not For You", "Tat Twam Asi", "Let You Be",
              "Breakup with My Ego", "Awaken the Lights", "Life Vest"]


def key(s):
    """Comparison key: case, spacing and apostrophe style ignored."""
    s = s.replace("’", "'").replace("‘", "'")
    return re.sub(r"\s+", " ", s).strip().lower()


def is_title(line):
    return key(line) in {key(t) for t in ALL_TITLES}


def pdf_songs():
    txt = subprocess.run(["pdftotext", "-layout", str(PDF), "-"], capture_output=True,
                         text=True, check=True).stdout
    songs, cur = {}, None
    for page in txt.split("\f"):
        body = [l.strip() for l in page.split("\n")]
        nonblank = [l for l in body if l]
        if len(nonblank) == 1 and is_title(nonblank[0]):      # title-only page starts a song
            cur = next(t for t in ALL_TITLES if key(t) == key(nonblank[0]))
            songs[cur] = []
            continue
        if cur is None or not nonblank:
            continue
        while body and not body[0]:
            body.pop(0)
        if not songs[cur] and body and key(body[0]) == key(cur):   # repeated title on first lyrics page
            body.pop(0)
        while body and not body[0]:
            body.pop(0)
        while body and not body[-1]:                             # page-end blanks are not verse breaks
            body.pop()
        songs[cur].append(body)
    return songs


def docx_lines(title):
    import docx  # python-docx
    paras = [p.text.strip() for p in docx.Document(str(DOCX)).paragraphs]
    starts = [i for i, p in enumerate(paras) if is_title(p)]
    first = next(i for i in starts if key(paras[i]) == key(title))
    nxt = next((i for i in starts if i > first + 1 and key(paras[i]) != key(title)), len(paras))
    block = paras[first:nxt]
    while block and (is_title(block[0]) or not block[0]):
        block.pop(0)
    while block and not block[-1]:
        block.pop()
    return block


def stanzas_from(lines):
    out, cur = [], []
    for l in lines:
        if l:
            cur.append(l)
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def draft_says_break(draft, a, b):
    """True/False if the draft has a/b adjacent with/without a blank between (consistently); None if absent."""
    seen = []
    for i, l in enumerate(draft):
        if key(l) != key(a):
            continue
        j, blank = i + 1, False
        while j < len(draft) and not draft[j]:
            blank, j = True, j + 1
        if j < len(draft) and key(draft[j]) == key(b):
            seen.append(blank)
    if not seen:
        return None
    if len(set(seen)) > 1:
        sys.exit(f"STOP: the draft is inconsistent about a break between {a!r} / {b!r}")
    return seen[0]


def main():
    songs = pdf_songs()
    result, report = {}, []
    for title, (slug, track) in SONGS.items():
        pages = songs[title]
        draft = docx_lines(title)
        stanzas = stanzas_from(pages[0])
        for nxt in pages[1:]:
            ns = stanzas_from(nxt)
            a, b = stanzas[-1][-1], ns[0][0]
            brk = draft_says_break(draft, a, b)
            if brk is None:
                sys.exit(f"STOP {title}: page break between {a!r} / {b!r} not found in the draft — decide by hand")
            report.append(f"{title}: page break {a!r} | {b!r} -> {'verse break' if brk else 'same verse'}")
            if brk:
                stanzas += ns
            else:
                stanzas[-1] += ns[0]
                stanzas += ns[1:]
        stanzas = [[l.replace("'", "’") for l in st] for st in stanzas]
        result[slug] = {"title": title, "track": track, "stanzas": stanzas}
        pdf_shape = [len(st) for st in stanzas]
        draft_shape = [len(st) for st in stanzas_from(draft)]
        pdf_flat = [key(l) for st in stanzas for l in st]
        draft_flat = [key(l) for l in draft if l]
        diff = [d for d in difflib.unified_diff(draft_flat, pdf_flat, "july-draft", "album-pdf", lineterm="", n=0)
                if d[:1] in "+-" and not d.startswith(("+++", "---"))]
        report.append(f"{title}: {len(stanzas)} verses, {len(pdf_flat)} lines\n"
                      f"     verse shape  PDF   {pdf_shape}\n"
                      f"     verse shape  draft {draft_shape}" + ("   (same)" if pdf_shape == draft_shape else "   ⚠ DIFFERENT")
                      + f"\n     word differences vs July draft: {len(diff)} line(s)"
                      + "".join("\n       " + d for d in diff))
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n".join(report))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
