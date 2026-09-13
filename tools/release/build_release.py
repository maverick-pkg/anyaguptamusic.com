#!/usr/bin/env python3
"""Build the Becoming release version of anyaguptamusic.com (branch release-becoming).

Creates
  songs/{not-for-you,let-you-be,breakup-with-my-ego,life-vest}/index.html
  becoming/index.html
  assets/photos/nfy-1587.jpg, assets/photos/becoming-1637.jpg   (staged, metadata-free)
Edits (every edit asserts its old text is present exactly as expected)
  index.html, epk/index.html, presave/, subscribed/, sitemap.xml, 3 live lyrics pages
Writes (Dropbox, outside the repo)
  Music/Anya/YouTube/SEPT 18 SWAP/description - <song> - OUT NOW.txt  (4 new songs)
  fixes "7 songs i wrote" -> "7 songs i co-wrote" in channel bio - OUT NOW.txt

Links that exist only after release stay as %%TOKENS%% (tools/release/links.json);
fill_links.py swaps them in on release night. /rsvp/ is NOT touched here — its
wording is being rewritten on main; flip it on release night.
Run from the repo root:  /usr/bin/python3 tools/release/build_release.py
"""
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REL = ROOT / "tools/release"
HOME = Path.home()
STAGED = HOME / "Dropbox (Personal)/Music/Anya/Professional photoshoot July2026/Not for you/Website release-day"
SWAP = HOME / "Dropbox (Personal)/Music/Anya/YouTube/SEPT 18 SWAP"
SITE = "https://anyaguptamusic.com"
LYR = json.loads((REL / "lyrics.json").read_text(encoding="utf-8"))

WRITERS = "Anya Gupta, Sarah Simmons and Greg Langston"
COMPOSERS = ["Anya Gupta", "Sarah Simmons", "Greg Langston"]
# (track, display title, schema name, slug, tag on the album page)
TRACKS = [
    (1, "You’re Original", "You're Original", "youre-original", "radio single"),
    (2, "Not For You", "Not For You", "not-for-you", "focus track"),
    (3, "Tat Twam Asi", "Tat Twam Asi", "tat-twam-asi", "single"),
    (4, "Let You Be", "Let You Be", "let-you-be", ""),
    (5, "Breakup with My Ego", "Breakup with My Ego", "breakup-with-my-ego", ""),
    (6, "Awaken the Lights", "Awaken the Lights", "awaken-the-lights", "single"),
    (7, "Life Vest", "Life Vest", "life-vest", ""),
]
NEW = {"not-for-you", "let-you-be", "breakup-with-my-ego", "life-vest"}
HASHTAG = {"not-for-you": "NotForYou", "let-you-be": "LetYouBe",
           "breakup-with-my-ego": "BreakupWithMyEgo", "life-vest": "LifeVest"}


def tok(kind, slug):
    return "%%" + kind + "_" + slug.upper().replace("-", "_") + "%%"


def dumps(obj):
    # same compact style the site already uses: "key": "value","next": ...
    return json.dumps(obj, ensure_ascii=False, separators=(",", ": "))


def read(rel):
    """Always start from the LIVE version on main, so the build can be re-run safely and
    picks up anything changed on main since (merge main into this branch first)."""
    import subprocess
    return subprocess.run(["git", "-C", str(ROOT), "show", f"main:{rel}"], capture_output=True,
                          text=True, check=True).stdout


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print("  wrote", rel)


def edit(text, old, new, count=1, where=""):
    """Replace old with new, asserting old occurs exactly `count` times.
    Idempotent: if old is absent but new is already present, leave it."""
    n = text.count(old)
    if n == 0 and new and new in text:
        return text
    if n != count:
        raise SystemExit(f"STOP {where}: expected {count}x, found {n}x of:\n  {old[:140]!r}")
    return text.replace(old, new)


# ---------------------------------------------------------------- shared page parts
YO = read("songs/youre-original/index.html")
CSS = YO[YO.index("<style>") + 7: YO.index("</style>")]
ARTIST = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', YO, re.S).group(1))["byArtist"]
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700;1,900'
         '&family=Caveat:wght@500;600&family=Karla:wght@400;500;700&display=swap" rel="stylesheet">')
NAV = YO[YO.index('<nav aria-label="Main">'): YO.index("</nav>") + 6]
FOOTER = YO[YO.index("<footer>"): YO.index("</footer>") + 9]
GOAT = '<script data-goatcounter="https://anyaguptamusic.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>'
EXTRA_CSS = ("\n.polaroid.portrait img{aspect-ratio:2/3;object-position:50% 20%}"
             "\n.tl{list-style:none;margin:1.4rem 0 0}"
             "\n.tl li{display:flex;flex-wrap:wrap;gap:.35rem .9rem;align-items:baseline;padding:.6em 0;border-bottom:1px solid rgba(33,29,32,.1)}"
             "\n.tl li:last-child{border-bottom:0}"
             "\n.tl .n{font-weight:700;font-size:.78rem;letter-spacing:.2em;color:var(--ink-soft);min-width:2.2ch}"
             "\n.tl a{font-family:var(--serif);font-weight:700;font-size:1.2rem;text-decoration:none;border-bottom:2px solid var(--peach-deep)}"
             "\n.tl a:hover{color:#b85a28}"
             "\n.tl .tag{font-size:.68rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--ink-soft)}"
             "\n.album-intro{font-size:1.05rem;line-height:1.75;max-width:56ch}"
             "\n.album-note{margin-top:1.2rem;color:var(--ink-soft);max-width:56ch}"
             "\n.album-note a{border-bottom:2px solid var(--peach-deep);text-decoration:none}"
             "\n.second{margin-top:2.4rem;transform:rotate(1.6deg)}\n")
SONG_CLICKS = """<script>
(function(){
  function ev(n){ if(window.goatcounter && goatcounter.count) goatcounter.count({path:n, event:true}); }
  var song = location.pathname.replace(/\\/index\\.html$/,'').replace(/\\/+$/,'').split('/').pop();
  document.addEventListener('click', function(e){
    var a = e.target.closest('a'); if(!a || !a.href) return;
    if (a.href.indexOf('open.spotify.com/track') > -1) ev('spotify-' + song);
    else if (a.href.indexOf('open.spotify.com/album') > -1) ev('spotify-album-' + song);
    else if (a.href.indexOf('music.apple.com') > -1) ev('apple-' + song);
    else if (a.href.indexOf('distrokid.com/hyperfollow') > -1) ev('listen-' + song);
  }, true);
})();
</script>"""


def more_links(exclude):
    items = [f'    <a href="/songs/{s}/">{t}</a>' for _, t, _, s, _ in TRACKS if s != exclude]
    return '  <div class="more-links">\n' + "\n".join(items) + "\n  </div>"


def page(head_title, meta_desc, canon, og_type, og_title, og_desc, og_image, jsonld, body, clicks):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{head_title}</title>
<meta name="description" content="{meta_desc}">
<link rel="canonical" href="{canon}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Anya Gupta">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary">
{FONTS}
<script type="application/ld+json">{dumps(jsonld)}</script>
<style>{CSS}{EXTRA_CSS}</style>
</head>
<body>
{NAV}
{body}
{FOOTER}
{GOAT}
{clicks}
</body>
</html>
"""


# ---------------------------------------------------------------- 1. photos
def copy_photos():
    for src, dst in [("nfy-lyrics-page-1587.jpg", "assets/photos/nfy-1587.jpg"),
                     ("becoming-page-1637.jpg", "assets/photos/becoming-1637.jpg")]:
        shutil.copyfile(STAGED / src, ROOT / dst)
        print("  copied", dst)


# ---------------------------------------------------------------- 2. four lyrics pages
def song_pages():
    for slug in ["not-for-you", "let-you-be", "breakup-with-my-ego", "life-vest"]:
        d = LYR[slug]
        title = d["title"]
        focus = slug == "not-for-you"
        role = "the focus track from the debut album Becoming" if focus else "a song from the debut album Becoming"
        eyebrow = "Official lyrics · the focus track from Becoming" if focus else "Official lyrics · from the album Becoming"
        if focus:
            img = ('<div class="polaroid tape portrait">\n      <img src="/assets/photos/nfy-1587.jpg" width="1200" height="1800" '
                   'alt="Anya Gupta in pearl headphones, lowering her sunglasses">\n'
                   '      <span class="cap">Not For You · 2026</span>\n    </div>')
        else:
            img = ('<div class="polaroid tape">\n      <img src="/assets/covers/becoming.jpg" width="1500" height="1500" '
                   'alt="Becoming — album cover">\n      <span class="cap">Becoming · 2026</span>\n    </div>')
        stanzas_html = "\n".join("<p>" + "<br>\n".join(html.escape(l, quote=False) for l in st) + "</p>"
                                 for st in d["stanzas"])
        lyrics_text = "\n\n".join("\n".join(st) for st in d["stanzas"])
        url = f"{SITE}/songs/{slug}/"
        jsonld = {"@context": "https://schema.org", "@type": "MusicRecording", "name": title, "url": url,
                  "datePublished": "2026-09-18", "image": f"{SITE}/assets/covers/becoming.jpg",
                  "byArtist": ARTIST,
                  "inAlbum": {"@type": "MusicAlbum", "name": "Becoming", "url": f"{SITE}/becoming/"},
                  "inLanguage": "en",
                  "sameAs": [tok("SPOTIFY_TRACK", slug), tok("APPLE_TRACK", slug)],
                  "recordingOf": {"@type": "MusicComposition", "name": title,
                                  "lyrics": {"@type": "CreativeWork", "text": lyrics_text},
                                  "composer": [{"@type": "Person", "name": n} for n in COMPOSERS]}}
        body = f"""
<header class="song">
  <div class="wrap">
    <span class="eyebrow">{eyebrow}</span>
    <h1>{title}</h1>
  </div>
</header>

<div class="wrap song-grid">
  <div class="cover-col">
    {img}
    <div class="cta-row">
      <a class="btn btn-solid" href="{tok('SPOTIFY_TRACK', slug)}" target="_blank" rel="noopener">Spotify</a>
      <a class="btn btn-line" href="{tok('APPLE_TRACK', slug)}" target="_blank" rel="noopener">Apple Music</a>
      <a class="btn btn-line" href="/becoming/">The album</a>
    </div>
  </div>
  <article class="lyrics-sheet">
    <span class="lead-script">from the heart, word for word ✦</span>
    <div class="lyrics">
{stanzas_html}
    </div>
    <p class="writers-line">Written by {WRITERS}</p>
    <p class="copyright-line">Lyrics © 2026 · all rights reserved</p>
  </article>
</div>

<section class="more wrap">
  <div class="h">More lyrics</div>
{more_links(slug)}
</section>
"""
        write(f"songs/{slug}/index.html", page(
            f"{title} Lyrics — Anya Gupta",
            f"Official lyrics to “{title}” by Anya Gupta — {role}. Read the full lyrics and listen to the song.",
            url, "music.song", f"{title} — official lyrics",
            f"Read the official lyrics to “{title}” by Anya Gupta and listen to the song.",
            f"{SITE}/assets/covers/becoming.jpg", jsonld, body, SONG_CLICKS))


# ---------------------------------------------------------------- 3. album page
def album_page():
    items = []
    for n, t, _, s, tag in TRACKS:
        tag_html = f'<span class="tag">{tag}</span>' if tag else ""
        items.append(f'        <li><span class="n">{n:02d}</span><a href="/songs/{s}/">{t}</a>{tag_html}</li>')
    jsonld = {"@context": "https://schema.org", "@type": "MusicAlbum", "name": "Becoming", "url": f"{SITE}/becoming/",
              "image": f"{SITE}/assets/covers/becoming.jpg", "datePublished": "2026-09-18", "numTracks": 7,
              "albumProductionType": "https://schema.org/StudioAlbum",
              "albumReleaseType": "https://schema.org/AlbumRelease",
              "byArtist": ARTIST, "sameAs": ["%%SPOTIFY_ALBUM%%", "%%APPLE_ALBUM%%"],
              "track": {"@type": "ItemList", "numberOfItems": 7, "itemListElement": [
                  {"@type": "ListItem", "position": n,
                   "item": {"@type": "MusicRecording", "name": sn, "url": f"{SITE}/songs/{s}/"}}
                  for n, _, sn, s, _ in TRACKS]}}
    body = f"""
<header class="song">
  <div class="wrap">
    <span class="eyebrow">The debut album · out now</span>
    <h1>Becoming</h1>
    <span class="subtitle">by Anya Gupta</span>
  </div>
</header>

<div class="wrap song-grid">
  <div class="cover-col">
    <div class="polaroid tape">
      <img src="/assets/covers/becoming.jpg" width="1500" height="1500" alt="Becoming — album cover: Anya Gupta with a coral rose in her hair, holding a microphone">
      <span class="cap">Becoming · 2026</span>
    </div>
    <div class="cta-row">
      <a class="btn btn-solid" href="%%SPOTIFY_ALBUM%%" target="_blank" rel="noopener">Spotify</a>
      <a class="btn btn-line" href="%%APPLE_ALBUM%%" target="_blank" rel="noopener">Apple Music</a>
      <a class="btn btn-line" href="%%LISTEN_URL%%" target="_blank" rel="noopener">More ways to listen</a>
    </div>
    <div class="polaroid tape portrait second">
      <img src="/assets/photos/becoming-1637.jpg" width="1200" height="1800" loading="lazy" decoding="async" alt="Anya Gupta from behind, arms raised, in an orange ANYA 22 jersey">
      <span class="cap">the Becoming era ✦</span>
    </div>
  </div>
  <article class="lyrics-sheet">
    <span class="lead-script">seven songs, all heart ✦</span>
    <p class="album-intro">Seven songs about self-love, individuality, and the light we all carry — featuring the focus track <b>“Not For You”</b> and the radio single <b>“You’re Original.”</b> Tap any song for its lyrics.</p>
    <ol class="tl">
{chr(10).join(items)}
    </ol>
    <p class="album-note">All seven songs are co-written by Anya Gupta, Sarah Simmons and Greg Langston, with Himani Gupta also co-writing “Tat Twam Asi.”</p>
    <p class="album-note">Every song has an official lyric video — <a href="https://www.youtube.com/@theanyagupta" target="_blank" rel="noopener">watch on YouTube</a>.</p>
  </article>
</div>
"""
    clicks = SONG_CLICKS.replace("var song = location.pathname.replace(/\\/index\\.html$/,'').replace(/\\/+$/,'').split('/').pop();",
                                 "var song = 'album-page';")
    write("becoming/index.html", page(
        "Becoming — the debut album by Anya Gupta",
        "Becoming, the debut album by Memphis pop singer-songwriter Anya Gupta — seven songs about self-love, "
        "individuality, and the light we all carry. Listen, and read the lyrics to every song.",
        f"{SITE}/becoming/", "music.album", "Becoming — the debut album by Anya Gupta",
        "Seven songs about self-love, individuality, and the light we all carry — featuring the focus track "
        "Not For You and the radio single You're Original.",
        f"{SITE}/assets/covers/becoming.jpg", jsonld, body, clicks))


# ---------------------------------------------------------------- 4. homepage
def homepage():
    s = read("index.html")
    w = "index.html"
    s = edit(s, "<title>Anya Gupta — Official Site · Becoming, the debut album September 18, 2026</title>",
             "<title>Anya Gupta — Official Site · Becoming, the debut album, out now</title>", where=w)
    s = edit(s, "Debut album Becoming arrives September 18, 2026 — featuring",
             "Debut album Becoming is out now — featuring", where=w)
    s = edit(s, "Anya Gupta — Becoming, the debut album · September 18, 2026",
             "Anya Gupta — Becoming, the debut album · out now", count=2, where=w)

    # structured data
    m = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', s, re.S)
    g = json.loads(m.group(2))
    graph = g["@graph"]
    album = next(n for n in graph if n.get("@type") == "MusicAlbum")
    if "url" not in album:
        new_album = {}
        for k, v in album.items():
            new_album[k] = v
            if k == "name":
                new_album["url"] = f"{SITE}/becoming/"
                new_album["sameAs"] = ["%%SPOTIFY_ALBUM%%", "%%APPLE_ALBUM%%"]
        album.clear()
        album.update(new_album)
    by_name = {sn: s_ for _, _, sn, s_, _ in TRACKS}
    for li in album["track"]["itemListElement"]:
        it = li["item"]
        name = it["name"].replace("’", "'")
        slug = by_name[name]
        it["url"] = f"{SITE}/songs/{slug}/"
        if slug in NEW:
            it["sameAs"] = [tok("SPOTIFY_TRACK", slug), tok("APPLE_TRACK", slug)]
    for n in graph:
        if n.get("@type") == "VideoObject" and "out September 18, 2026" in n.get("description", ""):
            n["description"] = n["description"].replace("out September 18, 2026", "released September 18, 2026")
    if not any(n.get("@type") == "VideoObject" and "Not For You" in n.get("name", "") for n in graph):
        pos = max(i for i, n in enumerate(graph) if n.get("@type") == "VideoObject") + 1
        graph.insert(pos, {
            "@type": "VideoObject", "name": "Anya Gupta — Not For You (Official Lyric Video)",
            "description": "The official lyric video for “Not For You,” the focus track from Becoming, Anya Gupta's debut album.",
            "uploadDate": "%%NFY_VIDEO_UPLOAD_DATE%%", "duration": "PT3M16S",
            "thumbnailUrl": "https://i.ytimg.com/vi/%%NFY_VIDEO_ID%%/maxresdefault.jpg",
            "embedUrl": "https://www.youtube-nocookie.com/embed/%%NFY_VIDEO_ID%%",
            "contentUrl": "https://www.youtube.com/watch?v=%%NFY_VIDEO_ID%%",
            "publisher": {"@id": f"{SITE}/#artist"}})
    s = s[:m.start(2)] + dumps(g) + s[m.end(2):]

    # hero
    s = edit(s, '<span class="strip eyebrow">The debut album · September 18</span>',
             '<span class="strip eyebrow">The debut album · out now</span>', where=w)
    s = edit(s, '      <div class="count" aria-live="polite">\n        <b id="days">—</b><span>days until the album</span>\n      </div>\n',
             "", where=w)
    s = edit(s, '<a class="btn btn-solid" href="https://distrokid.com/hyperfollow/anyagupta1/becoming" target="_blank" rel="noopener">Pre-save the album</a>',
             '<a class="btn btn-solid" href="%%LISTEN_URL%%" target="_blank" rel="noopener">Listen to Becoming</a>', where=w)
    old_tick = ('<span class="n">Becoming</span> · the debut album · september 18 · focus track <span class="g">Not For You</span>'
                ' · radio single <span class="g">You’re Original</span> · join the list · &nbsp;')
    new_tick = ('<span class="n">Becoming</span> · the debut album · out now · stream it everywhere · focus track '
                '<span class="g">Not For You</span> · radio single <span class="g">You’re Original</span> · &nbsp;')
    s = edit(s, old_tick, new_tick, count=2, where=w)

    # music: the focus-track panel becomes the album panel (keeps the Not For You story)
    i = s.find('    <div class="focus-mod tape rv">')
    j = s.find('    <div class="singles">')
    if "Pre-save Becoming</a>" in s[i:j]:
        s = s[:i] + """    <div class="focus-mod tape rv">
      <img src="assets/covers/becoming.jpg" alt="Becoming — debut album cover: Anya Gupta with a coral rose in her hair, holding a microphone" width="660" height="660" loading="lazy" decoding="async">
      <div class="fm-copy">
        <span class="fm-eyebrow">The debut album · out now</span>
        <h3>Becoming</h3>
        <p>Seven songs about self-love, individuality, and the light we all carry. The focus track, <b>“Not For You,”</b> is upbeat pop-rock about refusing to change yourself for anyone else — driven by electric guitar and live drums.</p>
        <div class="cta-row">
          <a class="btn btn-solid" href="%%SPOTIFY_ALBUM%%" target="_blank" rel="noopener">Listen on Spotify</a>
          <a class="btn btn-line" href="%%APPLE_ALBUM%%" target="_blank" rel="noopener">Apple Music</a>
          <a class="btn btn-line" href="becoming/">Album &amp; lyrics</a>
        </div>
      </div>
    </div>
""" + s[j:]
    elif "The debut album · out now</span>\n        <h3>Becoming</h3>" not in s:
        raise SystemExit("STOP index.html: focus-mod block not in the expected state")

    # tracklist
    s = edit(s, "<h3>Becoming · the tracklist · September 18</h3>", "<h3>Becoming · the tracklist</h3>", where=w)
    old_li = """        <li><span class="lock">01 · out now</span><a href="songs/youre-original/">You’re Original</a></li>
        <li><span class="lock">02 · focus track ✦</span>Not For You</li>
        <li><span class="lock">03 · out now</span><a href="songs/tat-twam-asi/">Tat Twam Asi</a></li>
        <li><span class="lock">04 ✦</span>Let You Be</li>
        <li><span class="lock">05 ✦</span>Breakup with My Ego</li>
        <li><span class="lock">06 · out now</span><a href="songs/awaken-the-lights/">Awaken the Lights</a></li>
        <li><span class="lock">07 ✦</span>Life Vest</li>"""
    new_li = "\n".join(
        f'        <li><span class="lock">{n:02d}{" · " + tag if tag in ("radio single", "focus track") else ""}</span>'
        f'<a href="songs/{sl}/">{t}</a></li>' for n, t, _, sl, tag in TRACKS)
    s = edit(s, old_li, new_li, where=w)
    s = edit(s, 'href="https://distrokid.com/hyperfollow/anyagupta1/becoming" target="_blank" rel="noopener" style="font-size:.78rem',
             'href="%%LISTEN_URL%%" target="_blank" rel="noopener" style="font-size:.78rem', where=w)
    s = edit(s, ">Pre-save Becoming on Spotify</a>", ">Listen to Becoming</a>", where=w)

    # video: the Not For You placeholder becomes the real lyric video
    old_vid = """      <a class="vid rv" href="https://distrokid.com/hyperfollow/anyagupta1/becoming" target="_blank" rel="noopener" aria-label="Not For You — focus track — visuals arrive September 18 — pre-save Becoming">
        <img loading="lazy" decoding="async" src="assets/photos/nfy-teaser.jpg" alt="">
        <div class="play" aria-hidden="true"><div class="ring">▶</div></div>
        <span class="soon">Visuals · Sep 18</span>
        <span class="label">Not For You — focus track</span>
      </a>"""
    new_vid = """      <div class="vid rv">
        <iframe src="https://www.youtube-nocookie.com/embed/%%NFY_VIDEO_ID%%" title="Anya Gupta — Not For You (Official Lyric Video)" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen style="width:100%;height:100%;border:0;display:block"></iframe>
      </div>"""
    s = edit(s, old_vid, new_vid, where=w)
    s = edit(s, "Official lyric videos for all three singles are here, along with a look inside the studio — the “Not For You” visuals premiere alongside the album. "
                '<a href="https://www.youtube.com/@theanyagupta" target="_blank" rel="noopener"><b>Subscribe on YouTube</b></a> to catch them the moment they drop.',
             "Official lyric videos for “Not For You” and all three singles are here, along with a look inside the studio. "
             'Every song on <i>Becoming</i> has a lyric video on YouTube — <a href="https://www.youtube.com/@theanyagupta" target="_blank" rel="noopener"><b>subscribe</b></a> for what’s next.',
             where=w)

    # about
    s = edit(s, "Her debut album <b><i>Becoming</i></b> arrives September 18: seven songs, including the singles",
             "Her debut album <b><i>Becoming</i></b> is out now: seven songs, including the focus track “Not For You” and the singles",
             where=w)

    # the countdown gate would throw once #days is gone — remove it
    a = s.find("// countdown to album day")
    b = s.find("// mailing list form posts directly to Mailchimp")
    if a != -1:
        seg = s[a:b]
        assert "release day: flip hero to out-now mode" in seg and seg.rstrip().endswith("})();"), "countdown block shape changed"
        s = s[:a] + s[b:]

    # click events: HyperFollow is now a listen link; count album links too
    s = edit(s, "if (h.indexOf('distrokid.com/hyperfollow') > -1) ev(a.closest('.focus-mod') ? 'presave-focus' : a.closest('.hero-copy') ? 'presave-hero' : a.closest('.upcoming') ? 'presave-tracklist' : 'presave');",
             "if (h.indexOf('distrokid.com/hyperfollow') > -1) ev(a.closest('.hero-copy') ? 'listen-hero' : a.closest('.upcoming') ? 'listen-tracklist' : 'listen');\n"
             "    else if (h.indexOf('open.spotify.com/album') > -1) ev(a.closest('.focus-mod') ? 'spotify-album-module' : 'spotify-album');",
             where=w)
    s = edit(s, "else if (h.indexOf('music.apple.com') > -1) ev('apple' + (song ? '-' + song : ''));",
             "else if (h.indexOf('music.apple.com') > -1) ev('apple' + (song ? '-' + song : (a.closest('.focus-mod') ? '-album-module' : '')));",
             where=w)

    # spacing the countdown used to provide; centred album buttons on phones
    css_add = ("/* release: hero spacing without the countdown; centred album buttons on phones */\n"
               ".hero-sub + .cta-row { margin-top:1.4rem }\n"
               "@media(max-width:640px){ .fm-copy .cta-row { justify-content:center } }\n")
    if css_add not in s:
        assert s.count("</style>") == 1
        s = s.replace("</style>", css_add + "</style>")
    write(w, s)


# ---------------------------------------------------------------- 5. press kit
def epk():
    s = read("epk/index.html")
    w = "epk/index.html"
    s = edit(s, 'Becoming</em> out September 18, 2026</div>', 'Becoming</em> out now</div>', where=w)
    s = edit(s, '<div class="meta">7 songs &middot; September 18, 2026</div>',
             '<div class="meta">7 songs &middot; Sept 18, 2026</div>', where=w)
    s = edit(s, "<em>Becoming</em>, releases September 18, 2026, featuring the singles",
             "<em>Becoming</em>, was released September 18, 2026, featuring the focus track &ldquo;Not For You&rdquo; and the singles",
             where=w)
    s = edit(s, "Becoming</em></b> &mdash; <b>7&nbsp;songs</b></div>",
             "Becoming</em></b> &mdash; <b>out now</b> &middot; 7&nbsp;songs</div>", where=w)
    s = edit(s, "<b><em>Becoming</em></b> &mdash; out September 18, 2026, led by the focus track",
             "<b><em>Becoming</em></b> &mdash; out now, led by the focus track", where=w)
    write(w, s)


# ---------------------------------------------------------------- 6. small pages + sitemap
def small_pages():
    s = read("presave/index.html")
    s = edit(s, "<title>Pre-save Becoming — Anya Gupta</title>", "<title>Listen to Becoming — Anya Gupta</title>", where="presave")
    s = edit(s, """<!-- REPOINT TARGET: replace both URLs below with the DistroKid HyperFollow link when available;
     on release day, repoint to the album smart link. One printed URL, many lives. -->""",
             """<!-- Printed on the party cards and posters: after release it points at the album's
     listen link (LISTEN_URL in tools/release/links.json). One printed URL, many lives. -->""", where="presave")
    s = edit(s, "https://distrokid.com/hyperfollow/anyagupta1/becoming", "%%LISTEN_URL%%", count=3, where="presave")
    s = edit(s, "encodeURIComponent('Pre-save redirect')", "encodeURIComponent('Listen redirect')", where="presave")
    write("presave/index.html", s)

    s = read("subscribed/index.html")
    s = edit(s, "The debut album <b>Becoming</b> arrives September 18.", "The debut album <b>Becoming</b> is out now.", where="subscribed")
    s = edit(s, '<a class="btn btn-solid" href="https://distrokid.com/hyperfollow/anyagupta1/becoming">Pre-save the album</a>',
             '<a class="btn btn-solid" href="%%LISTEN_URL%%">Listen to Becoming</a>', where="subscribed")
    write("subscribed/index.html", s)

    for slug in ["youre-original", "tat-twam-asi", "awaken-the-lights"]:
        rel = f"songs/{slug}/index.html"
        s = read(rel)
        new = more_links(slug)
        m = re.search(r'  <div class="more-links">\n.*?\n  </div>', s, re.S)
        assert m, rel
        s = s[:m.start()] + new + s[m.end():]
        write(rel, s)

    urls = [("/", "weekly"), ("/becoming/", None)] + [(f"/songs/{s}/", None) for _, _, _, s, _ in TRACKS]
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, freq in urls:
        out += ["  <url>", f"    <loc>{SITE}{path}</loc>", "    <lastmod>%%DEPLOY_DATE%%</lastmod>"]
        if freq:
            out.append(f"    <changefreq>{freq}</changefreq>")
        out.append("  </url>")
    out += ["  <url>", f"    <loc>{SITE}/privacy/</loc>", "    <lastmod>2026-08-20</lastmod>", "  </url>", "</urlset>"]
    write("sitemap.xml", "\n".join(out) + "\n")


# ---------------------------------------------------------------- 7. YouTube texts (Dropbox)
def youtube_texts():
    for slug in ["not-for-you", "let-you-be", "breakup-with-my-ego", "life-vest"]:
        d = LYR[slug]
        t = d["title"]
        lead = ("The focus track from Anya Gupta’s debut album \"Becoming,\" out now." if slug == "not-for-you"
                else "From Anya Gupta’s debut album \"Becoming,\" out now.")
        lyrics = "\n\n".join("\n".join(st) for st in d["stanzas"])
        txt = f"""{t} — the official lyric video.

{lead}

Listen to "Becoming"
Spotify: https://open.spotify.com/album/1ldpXvka3fAaIqdnWEMnot
All platforms: https://distrokid.com/hyperfollow/anyagupta1/becoming

Watch the album trailer: https://youtu.be/LwVfZLW1kKo

——————————

LYRICS

{lyrics}

——————————

Written by {WRITERS}
℗ 2026 Anya Gupta

Follow Anya
Website: https://anyaguptamusic.com
Instagram: https://instagram.com/anyagupta.music
TikTok: https://tiktok.com/@anyagupta.music
Facebook: https://facebook.com/61556419742590

#AnyaGupta #{HASHTAG[slug]} #Becoming
"""
        p = SWAP / f"description - {t} - OUT NOW.txt"
        p.write_text(txt, encoding="utf-8")
        print("  wrote", p.relative_to(HOME / "Dropbox (Personal)"), f"({len(txt)} chars)")
    bio = SWAP / "channel bio - OUT NOW.txt"
    b = bio.read_text(encoding="utf-8")
    if "7 songs i wrote." in b:
        bio.write_text(b.replace("7 songs i wrote.", "7 songs i co-wrote."), encoding="utf-8")
        print("  fixed", bio.name, "(i wrote -> i co-wrote)")


if __name__ == "__main__":
    print("photos");       copy_photos()
    print("lyrics pages"); song_pages()
    print("album page");   album_page()
    print("homepage");     homepage()
    print("press kit");    epk()
    print("small pages");  small_pages()
    print("youtube texts"); youtube_texts()
    print("done")
