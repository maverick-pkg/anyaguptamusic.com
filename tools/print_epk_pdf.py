#!/usr/bin/env python3
"""Print the press kit (epk/index.html) to PDF and put the copies where they are served.

The press-kit PDF lives in THREE places, and all three must match the page:
  epk/Anya Gupta EPK.pdf                           linked from /epk/
  assets/press/Anya-Gupta-EPK.pdf                  the homepage "Press kit (PDF)" link
  Dropbox Music/Anya/Biography/Anya Gupta EPK.pdf  only with --dropbox

  /usr/bin/python3 tools/print_epk_pdf.py [--dropbox]   print, check, then copy
  /usr/bin/python3 tools/print_epk_pdf.py --check       check only; exit 1 if the two repo
      copies differ or any line of the page's text is missing from the PDF (a stale PDF)

Nothing is copied unless the new PDF is one US-letter page, uses only the site's web
fonts, and carries every line of the page's text. Needs Google Chrome and poppler.
Headless Chrome sometimes writes the PDF and then never exits on this page, so the
script waits for a complete file and then stops that one process.
"""
import html
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "epk/index.html"
COPIES = [ROOT / "epk/Anya Gupta EPK.pdf", ROOT / "assets/press/Anya-Gupta-EPK.pdf"]
DROPBOX = Path.home() / "Dropbox (Personal)/Music/Anya/Biography/Anya Gupta EPK.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONTS = ("Karla", "PlayfairDisplay", "Caveat")


def tool(name):
    return shutil.which(name) or f"/opt/homebrew/bin/{name}"


def squash(s):
    """Compare text ignoring case, spacing and ligatures (letter-spaced caps, line wraps)."""
    return re.sub(r"\s+", "", unicodedata.normalize("NFKD", s).casefold())


def page_lines():
    """The page's visible text, one entry per block element (inline tags joined)."""
    s = PAGE.read_text(encoding="utf-8")
    s = s[s.index("<body"):]
    s = re.sub(r"<(script|style|svg)\b.*?</\1>|<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"</?(?:a|b|em|i|span|strong|small)\b[^>]*>", "", s)
    lines = (" ".join(html.unescape(c).split()) for c in re.split(r"<[^>]+>", s))
    return [l for l in lines if l]


def problems(pdf):
    out = []
    info = subprocess.run([tool("pdfinfo"), str(pdf)], capture_output=True, text=True).stdout
    if not re.search(r"^Pages:\s+1$", info, re.M):
        out.append("not exactly one page")
    if "612 x 792" not in info:
        out.append("not US-letter size")
    rows = subprocess.run([tool("pdffonts"), str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
    names = {r.split()[0].split("+")[-1] for r in rows if r.strip()}
    stray = sorted(n for n in names if not n.startswith(FONTS))
    if stray:
        out.append(f"fallback fonts (web fonts did not load?): {stray}")
    out += [f"font {f} missing" for f in FONTS if not any(n.startswith(f) for n in names)]
    text = squash(subprocess.run([tool("pdftotext"), "-raw", str(pdf), "-"], capture_output=True,
                                 text=True, check=True).stdout)
    gone = [l for l in page_lines() if squash(l) not in text]
    if gone:
        out.append(f"page text missing from the PDF: {gone[:4]}")
    return out


def print_pdf(dest):
    tmp = Path(tempfile.mkdtemp(prefix="epk-print-"))
    out = tmp / "epk.pdf"
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
         f"--user-data-dir={tmp / 'profile'}", "--no-pdf-header-footer", "--virtual-time-budget=8000",
         f"--print-to-pdf={out}", PAGE.as_uri()],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        size, deadline = -1, time.time() + 90
        while True:
            time.sleep(1)
            now = out.stat().st_size if out.exists() else -1
            if now > 0 and now == size and \
                    subprocess.run([tool("pdfinfo"), str(out)], capture_output=True).returncode == 0:
                break
            if proc.poll() is not None and now <= 0:
                raise SystemExit("Chrome exited without writing the PDF")
            if time.time() > deadline:
                raise SystemExit("timed out waiting for Chrome to write the PDF")
            size = now
        shutil.copyfile(out, dest)
    finally:
        if proc.poll() is None:
            proc.terminate()  # only the process started above — never stop Chrome by name
            try:
                proc.wait(10)
            except subprocess.TimeoutExpired:
                proc.kill()
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if "--check" in sys.argv:
        bad = []
        if COPIES[0].read_bytes() != COPIES[1].read_bytes():
            bad.append(f"{COPIES[1].relative_to(ROOT)} differs from {COPIES[0].relative_to(ROOT)}")
        bad += [f"{COPIES[0].relative_to(ROOT)}: {p}" for p in problems(COPIES[0])]
        print("\n".join("✗ " + b for b in bad) if bad else "✓ press-kit PDFs match the page")
        sys.exit(1 if bad else 0)

    new = Path(tempfile.mkdtemp(prefix="epk-new-")) / "Anya Gupta EPK.pdf"
    print_pdf(new)
    bad = problems(new)
    if bad:
        raise SystemExit("✗ nothing copied — " + "; ".join(bad) + f"\n  (the print is at {new})")
    dests = COPIES + ([DROPBOX] if "--dropbox" in sys.argv else [])
    for d in dests:
        if not d.parent.is_dir():
            raise SystemExit(f"✗ folder missing: {d.parent}")
    for d in dests:
        shutil.copyfile(new, d)
        print("  wrote", d)
    shutil.rmtree(new.parent, ignore_errors=True)
    print("✓ press-kit PDF printed and checked")


if __name__ == "__main__":
    main()
