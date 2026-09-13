#!/usr/bin/env python3
"""Release night: fill tools/release/links.json from PUBLIC pages — no logins.

  Spotify  open.spotify.com/embed/album/<id>   -> the 7 track links (works only once the album is live)
  Apple    itunes.apple.com/lookup             -> album link + 4 track links
  YouTube  the channel's public feed           -> the Not For You lyric video id + publish date
  DEPLOY_DATE = today's date in Memphis

Only fills values that are still null (use --force to refresh). Prints what is still
missing; fill_links.py refuses to run until nothing it needs is missing.
Run:  /usr/bin/python3 tools/release/fetch_links.py
"""
import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

LINKS = Path(__file__).with_name("links.json")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"}
APPLE_ARTIST = "1728554823"            # ours; 1434780958 is the Boston Anya Gupta — never use
YT_CHANNEL = "UCuwOWqWqr2lADhOmn-w985A"
NEW = {"Not For You": "NOT_FOR_YOU", "Let You Be": "LET_YOU_BE",
       "Breakup with My Ego": "BREAKUP_WITH_MY_EGO", "Life Vest": "LIFE_VEST"}
ORDER = ["You're Original", "Not For You", "Tat Twam Asi", "Let You Be",
         "Breakup with My Ego", "Awaken the Lights", "Life Vest"]


def key(s):
    return re.sub(r"\s+", " ", s.replace("’", "'")).strip().lower()


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
        return r.read().decode("utf-8", "replace")


def spotify(links, found):
    alb = links["SPOTIFY_ALBUM"].rstrip("/").split("/")[-1].split("?")[0]
    x = get(f"https://open.spotify.com/embed/album/{alb}")
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', x, re.S)
    ent = json.loads(m.group(1))["props"]["pageProps"]["state"]["data"]["entity"] if m else {}
    tracks = ent.get("trackList") or []
    if not tracks:
        print("  Spotify: album not live yet (embed page has no tracks)")
        return
    titles = [t.get("title", "") for t in tracks]
    if [key(t) for t in titles] != [key(t) for t in ORDER]:
        print("  Spotify: ⚠ track titles/order differ from the canonical tracklist:", titles)
    for t in tracks:
        name = next((n for n in NEW if key(n) == key(t.get("title", ""))), None)
        if name:
            found[f"SPOTIFY_TRACK_{NEW[name]}"] = "https://open.spotify.com/track/" + t["uri"].split(":")[-1]


def apple(found):
    d = json.loads(get(f"https://itunes.apple.com/lookup?id={APPLE_ARTIST}&entity=album&limit=200"))
    albums = [r for r in d.get("results", []) if r.get("wrapperType") == "collection" and key(r.get("collectionName", "")) == "becoming"]
    if not albums:
        print("  Apple: album not listed yet")
        return
    a = albums[0]
    found["APPLE_ALBUM"] = a["collectionViewUrl"].split("?")[0]
    d = json.loads(get(f"https://itunes.apple.com/lookup?id={a['collectionId']}&entity=song&limit=50"))
    for r in d.get("results", []):
        if r.get("wrapperType") != "track":
            continue
        name = next((n for n in NEW if key(n) == key(r.get("trackName", ""))), None)
        if name:
            u = r["trackViewUrl"]
            base, _, q = u.partition("?")
            i = re.search(r"(?:^|&)i=(\d+)", q)
            found[f"APPLE_TRACK_{NEW[name]}"] = base + (f"?i={i.group(1)}" if i else "")


def youtube(found):
    x = get(f"https://www.youtube.com/feeds/videos.xml?channel_id={YT_CHANNEL}")
    for vid, title, pub in re.findall(r"<yt:videoId>([^<]+)</yt:videoId>.*?<title>([^<]+)</title>.*?<published>([^<]+)</published>", x, re.S):
        if "not for you" in key(title) and "lyric" in key(title):
            found["NFY_VIDEO_ID"] = vid
            found["NFY_VIDEO_UPLOAD_DATE"] = pub[:10]
            return
    print("  YouTube: Not For You lyric video not public yet")


def main():
    force = "--force" in sys.argv
    links = json.loads(LINKS.read_text())
    found = {}
    for step in (lambda: spotify(links, found), lambda: apple(found), lambda: youtube(found)):
        try:
            step()
        except Exception as e:  # keep going; report
            print("  ⚠", type(e).__name__, e)
    found.setdefault("DEPLOY_DATE", (datetime.now(timezone.utc) - timedelta(hours=5)).strftime("%Y-%m-%d"))
    for k, v in found.items():
        if links.get(k) is None or force:
            links[k] = v
    LINKS.write_text(json.dumps(links, indent=2) + "\n")
    print("\nlinks.json now:")
    for k, v in links.items():
        if not k.startswith("_"):
            print(f"  {'✓' if v else '·'} {k:34} {v or 'MISSING'}")


if __name__ == "__main__":
    main()
