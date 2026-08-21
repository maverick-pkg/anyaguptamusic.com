# RSVP backend — one-time deploy (~5 minutes)

The `/rsvp` page posts to a Google Apps Script web app running on the family
Google account. The script records every RSVP + photo permission in a private
Google Sheet, shows the venue to every attending RSVP, and emails them a
confirmation with a calendar invite.

**Policy (user ruling 2026-08-19):** no guest-roster gate — every attending
submission gets the venue automatically. Protection is detection, not
prevention: every submission writes a timestamped row and (optionally) sends
you a notify email, and the RSVPs tab doubles as the door list.

**Privacy invariant (this repo is public):** the real venue address is typed
ONLY into the Apps Script `CONFIG` — never into this repo.

## Steps

1. In the family Google account, create a new Google Sheet named
   **Becoming Party RSVPs** (it stays private — don't share it).
2. In the Sheet: **Extensions → Apps Script**. Delete whatever is in the
   editor and paste in the full contents of `Code.gs` from this folder.
3. At the top of the pasted code, edit the values already there in `CONFIG`:
   - `VENUE_NAME` and `VENUE_ADDRESS` — the real venue (only here!).
   - `NOTIFY` — your own email for a heads-up message per RSVP
     (recommended: the gmail). Leave `''` for Sheet-only.
   (Until the two venue placeholders are replaced, the deployed form
   answers "we'll email you the details" instead of revealing anything.)
4. In the editor toolbar, select the function **`setup`** and press **Run**.
   First time: approve the authorization prompts (Sheets + email — it writes
   rows and sends the confirmations). This creates the `RSVPs` tab with its
   header row. Re-running it later is safe; it only rewrites the headers.
   (A leftover `GuestList` tab from the earlier roster-gated version can be
   deleted — right-click the tab → Delete. It is ignored either way.)
5. **Deploy → New deployment → Web app**.
   - Execute as: **Me**.
   - Who has access: **Anyone**. (Required so parents can submit without a
     Google login. The URL only accepts RSVP submissions — it can't read the
     Sheet.)
   - Click Deploy and copy the **Web app URL** (ends in `/exec`).
6. Put that URL into `rsvp/index.html` — the empty `content=""` in:
   `<meta name="rsvp-endpoint" content="">` — commit and push.
   (Until the URL is in place, the page falls back to a pre-filled email
   RSVP, so nothing is ever broken.)

## Test before invites go out

- Submit an attending RSVP with your own email → venue appears on screen and
  the confirmation email (with .ics attached) arrives.
- Submit a regrets RSVP → thank-you screen, no venue.
- Check both rows landed in the Sheet with the right photo-permission
  values, then delete the test rows.

## Editing the script later

Use **Deploy → Manage deployments → ✏️ edit → Version: New version → Deploy**.
That keeps the SAME `/exec` URL. ("New deployment" would mint a different URL
and the site would need a commit.)

## Tracking photo consent

Every form submission writes `YES` or `NO` in **column F ("Photo permission")**
of the RSVPs tab. To make that readable at a glance and get a live
photographer's list, paste `consent-tracker.gs` (this folder) at the BOTTOM of
the existing `Code.gs` — do **not** replace the file, that would wipe your
CONFIG venue values — then run **`installConsentTracking`** once from the
function dropdown. Running a function in the editor does not require
redeploying; the live `/exec` URL is unaffected.

It color-codes column F and adds a **PHOTO CONSENT** tab with live counts, a
CLEARED list, and a DO NOT PUBLISH list.

⚠ RSVPs that arrive **outside the form never touch the sheet** and carry no
consent — someone using the page's "form not working, email us" fallback, the
site's booking email, or just replying to whatever message carried the invite.
The circulating invite card points only at the RSVP page, so this should be
rare. When it happens, add the family as a row on the RSVPs tab by hand (put
YES or NO in column F once you've asked the parent) — the PHOTO CONSENT tab
picks up manual rows automatically.

## After the party

- The PHOTO CONSENT tab's CLEARED column is the photographer's list
  (export it for them before the event).
- The Sheet is the consent record — keep it until the photo album is settled,
  then archive/delete per the privacy page.
