# Release day — September 18, 2026 (Friday)

The site flips itself at local midnight (hero, lower CTA, ticker) via the countdown gate in
`index.html`. Everything below is the **deploy** that makes the flip permanent and complete.
Work the list top to bottom; push once; verify live.

## 1. Links
- [ ] `presave/index.html` — replace all THREE HyperFollow URLs with the album smart link (HyperFollow auto-converts, but the site should point at the canonical album page).
- [ ] `subscribed/index.html` — "Pre-save the album" → "Listen to Becoming" + smart link.
- [ ] Hero CTA `index.html` — hardcode "Listen to Becoming" (gate text becomes permanent).
- [ ] `.upcoming` pre-save link → "Listen to Becoming".

## 2. Homepage copy + structure
- [ ] Hero eyebrow "The debut album · out now"; `.count` block removed.
- [ ] Ticker: "Becoming · out now · stream it everywhere · Not For You · You're Original".
- [ ] Tracklist: remove ✦ locks; all seven link to their lyrics pages.
- [ ] Focus-track module: CTA → "Listen to 'Not For You'" + track link; keep the story copy.
- [ ] Music section: add the **Becoming album card** (assets/covers/becoming.jpg) FIRST, then **Not For You** card before the three older singles.
- [ ] Video section: "Becoming — sessions" card → the real premiere/playlist URL (never the generic channel once it exists).

## 3. Meta + structured data (crawlers don't run JS — must be in the deploy)
- [ ] `<title>`, meta description, og:title/description, twitter:title/description → "out now" copy, both roles kept.
- [ ] MusicAlbum JSON-LD: add `url` + `sameAs` with the live Spotify + Apple ALBUM URLs; add MusicRecording entries for the four new tracks with their URLs.
- [ ] Verify both Anya Gupta Apple IDs: OURS = artist 1728554823 (the other 1434780958 is the Boston artist).

## 4. Lyrics pages (generator: build_lyrics_pages.py pattern — regenerate from user-supplied docs)
- [ ] /songs/not-for-you/ · /songs/let-you-be/ · /songs/breakup-with-my-ego/ · /songs/life-vest/ (slugs from canonical spellings).
- [ ] Each with full MusicGroup entity + sameAs, Spotify/Apple track links, exit events, GoatCounter snippet.
- [ ] Homepage tracklist links + sitemap entries + `lastmod`.
- [ ] NFY page headline art = frame 1587 (family-approved) — strip EXIF.

## 5. Album page
- [ ] Build `/becoming/` — cover, tracklist, all seven lyrics links, listen links, credits only if splits are final. Add to sitemap.

## 6. EPK (three PDF locations!)
- [ ] `epk/index.html`: lines saying "out September 18, 2026" → "out now" / "released September 18, 2026"; singles note; stats tile date.
- [ ] Regenerate PDF → `epk/Anya Gupta EPK.pdf` AND `assets/press/Anya-Gupta-EPK.pdf` AND Dropbox `Music/Anya/Biography/Anya Gupta EPK.pdf`.

## 7. Off-site, same day
- [ ] DistroKid / HyperFollow bio: "arrives September 18" → out now.
- [ ] Google Search Console: URL Inspection → Request indexing for /, /becoming/, four new song pages.
- [ ] GoatCounter: confirm `presave-*` events drop and `spotify-*`/`apple-*` rise — that's the flip working.

## 8. September 26 (her birthday)
- [ ] If age stays on the site: "fifteen-year-old" → "sixteen-year-old" in index.html About + epk/index.html (+ PDF ×3) + HyperFollow bio.
