# Release day — September 18, 2026 (Friday)

The site flips itself at local midnight (hero, lower CTA, ticker) via the countdown gate in
`index.html`. Everything below is the **deploy** that makes the flip permanent and complete.
Work the list top to bottom; push once; verify live.

> ⏰ **Timing (checked 2026-09-13).** DistroKid's HyperFollow page counts down to `00:00 UTC Sep 18` = **Thu Sep 17, 7:00 PM CDT**, and Spotify's campaign screens list the US release date as **Thursday, September 17**. The official date stays September 18 — do not re-date anything — but check Spotify from **Thursday 7 PM CT** (again at 11 PM CT). The DSP links this list needs exist the moment it is live, so the work can start Thursday night. The countdown gate still flips at local midnight Sep 18; leave it — the pre-save links convert to listen links on their own.

## 1. Links
- [ ] `presave/index.html` — replace all THREE HyperFollow URLs with the album smart link (HyperFollow auto-converts, but the site should point at the canonical album page).
- [ ] `subscribed/index.html` — "Pre-save the album" → "Listen to Becoming" + smart link.
- [ ] Hero CTA `index.html` — hardcode "Listen to Becoming" (gate text becomes permanent).
- [ ] `.upcoming` pre-save link → "Listen to Becoming".
- [ ] `rsvp/index.html` (post-party thank-you page since 2026-09-13): "Becoming arrives September 18" → "Becoming is out now"; "Pre-save Becoming" → "Listen to Becoming".
- [ ] Shows section + Event JSON-LD: if the WREG Live at 9 airdate is known, the line reads the real date (eventStatus `EventRescheduled`, new `startDate`, `previousStartDate` 2026-09-11T09:00:00-05:00); once aired, replace with the replay embed/link.

## 2. Homepage copy + structure
- [ ] Hero eyebrow "The debut album · out now"; `.count` block removed.
- [ ] Ticker: "Becoming · out now · stream it everywhere · Not For You · You're Original".
- [ ] Tracklist: remove ✦ locks; all seven link to their lyrics pages.
- [ ] Focus-track module: CTA → "Listen to 'Not For You'" + track link; keep the story copy.
- [ ] Music section: add the **Becoming album card** (assets/covers/becoming.jpg) FIRST, then **Not For You** card before the three older singles.
- [ ] Video section: "Becoming — sessions" card → the real premiere/playlist URL (never the generic channel once it exists).
- [ ] Video section: NFY teaser card (assets/photos/nfy-teaser.jpg → hyperfollow) → replace with the real "Not For You" video embed; drop the "Visuals · Sep 18" badge.

## 3. Meta + structured data (crawlers don't run JS — must be in the deploy)
- [ ] `<title>`, meta description, og:title/description, twitter:title/description → "out now" copy, both roles kept.
- [ ] MusicAlbum JSON-LD: add `url` + `sameAs` with the live Spotify + Apple ALBUM URLs; add MusicRecording entries for the four new tracks with their URLs.
- [ ] Verify both Anya Gupta Apple IDs: OURS = artist 1728554823 (the other 1434780958 is the Boston artist).

## 4. Lyrics pages (generator: build_lyrics_pages.py pattern — regenerate from user-supplied docs)
- [ ] /songs/not-for-you/ · /songs/let-you-be/ · /songs/breakup-with-my-ego/ · /songs/life-vest/ (slugs from canonical spellings).
- [ ] Each with full MusicGroup entity + sameAs, Spotify/Apple track links, exit events, GoatCounter snippet.
- [ ] Writers line + composer schema on every new page. **Full roster confirmed 2026-09-07 — use exactly this, no percentages ever:**

| # | Song | Written by |
|---|------|-----------|
| 01 | You're Original | Anya Gupta, Sarah Simmons, Greg Langston *(live)* |
| 02 | Not For You | Anya Gupta, Sarah Simmons, Greg Langston |
| 03 | Tat Twam Asi | Anya Gupta, Sarah Simmons, Greg Langston, **Himani Gupta** *(live)* |
| 04 | Let You Be | Anya Gupta, Sarah Simmons, Greg Langston |
| 05 | Breakup with My Ego | Anya Gupta, Sarah Simmons, Greg Langston |
| 06 | Awaken the Lights | Anya Gupta, Sarah Simmons, Greg Langston *(live)* |
| 07 | Life Vest | Anya Gupta, Sarah Simmons, Greg Langston |

  Tat Twam Asi is the only track with a fourth writer. Copyright line stays "Lyrics © YYYY · all rights reserved" — no sole owner asserted.
- [ ] Homepage tracklist links + sitemap entries + `lastmod`.
- [ ] NFY page headline art = frame 1587 (family-approved) — web-ready file (EXIF/XMP/IPTC stripped) staged at Dropbox `Music/Anya/Professional photoshoot July2026/Not for you/Website release-day/nfy-lyrics-page-1587.jpg`.

## 5. Album page
- [ ] Build `/becoming/` — cover, tracklist, all seven lyrics links, listen links, credits only if splits are final. Add to sitemap.
- [ ] Page art: frame 1637 "ANYA 22" (family-approved) — web-ready file staged at Dropbox `Music/Anya/Professional photoshoot July2026/Not for you/Website release-day/becoming-page-1637.jpg`.

## 6. EPK (three PDF locations!)
- [ ] `epk/index.html`: lines saying "out September 18, 2026" → "out now" / "released September 18, 2026"; singles note; stats tile date.
- [ ] Regenerate PDF → `epk/Anya Gupta EPK.pdf` AND `assets/press/Anya-Gupta-EPK.pdf` AND Dropbox `Music/Anya/Biography/Anya Gupta EPK.pdf`.

## 7. Off-site, same day
- [ ] MusicBrainz: "Add release" on her artist entry (41ae3f66-2051-4641-b5d7-cbe0baafd27c) — album *Becoming*, RG type Album, Digital Media, 7 tracks in canonical order/spellings, date 2026-09-18, [Worldwide], [no label], Apple + Spotify album links. ⚠ artist autocomplete: pick "Memphis pop singer-songwriter", never "US | pop".
- [ ] DistroKid / HyperFollow bio: "arrives September 18" → out now.
- [ ] KOMI link-in-bio (anyaguptamusic.komi.io): "pre-save becoming" → the album listen link; page title → out-now. (Party blocks + the GuestCam link should already be gone — removed after the 09-12 party.)
- [ ] **Spotify for Artists bio** (artists.spotify.com → View Profile → About → Edit next to "More Info"): `my debut album "Becoming" is out september 18` → `is out now`. ⛔ Change ONLY those words — keep her lowercase voice, the ★ marks and the rest verbatim. It is her own writing, not campaign copy.
- [ ] Google Search Console: URL Inspection → Request indexing for /, /becoming/, four new song pages.
- [ ] GoatCounter: confirm `presave-*` events drop and `spotify-*`/`apple-*` rise — that's the flip working.

## 8. September 22 (her birthday)
- [ ] If age stays on the site: "fifteen-year-old" → "sixteen-year-old" in index.html About + epk/index.html (+ PDF ×3) + HyperFollow bio.
- [ ] **Spotify for Artists bio:** `i'm 15` → `i'm 16` — change only that, keep her voice verbatim. (Missing from this list until 2026-09-13; the bio gained "i'm 15" on 09-07.)
- [ ] Note: this falls 4 days AFTER release — a "sweet sixteen + debut album" post is an easy content beat.
