# RSVP backend — one-time deploy (~5 minutes)

The `/rsvp` page posts to a Google Apps Script web app running on the family
Google account. The script records every RSVP + photo permission in a private
Google Sheet, and when the child's name matches the guest roster it returns
the venue to the page and emails a confirmation with a calendar invite.

**Privacy invariants (this repo is public):**
- The real venue address is typed ONLY into the Apps Script `CONFIG` — never
  into this repo.
- The guest roster lives ONLY in the private Sheet's `GuestList` tab — never
  in this repo.

## Steps

1. In the family Google account, create a new Google Sheet named
   **Becoming Party RSVPs** (it stays private — don't share it).
2. In the Sheet: **Extensions → Apps Script**. Delete the placeholder code and
   paste in the full contents of `Code.gs` from this folder.
3. At the top of the pasted code, fill in `CONFIG`:
   - `VENUE_NAME` and `VENUE_ADDRESS` — the real venue (only here!).
   - `NOTIFY` — your own email if you want a heads-up message per RSVP
     (recommended: the gmail). Leave `''` for Sheet-only.
4. In the editor toolbar, select the function **`setup`** and press **Run**.
   Approve the authorization prompts (it asks for Sheets + email because the
   script writes rows and sends the confirmations). This creates the `RSVPs`
   and `GuestList` tabs.
5. Open the Sheet's **GuestList** tab and replace the two sample rows with the
   real roster — one invited child per row, "First Last". (The match also
   accepts a unique first name, so "Maddie Smith" matches a parent who types
   just "Maddie" — as long as only one Maddie is on the roster.)
6. Back in the editor: **Deploy → New deployment → Web app**.
   - Description: anything.
   - Execute as: **Me**.
   - Who has access: **Anyone**. (Required so parents can submit without a
     Google login. The URL only accepts RSVP submissions — it can't read the
     Sheet, and it only reveals the venue on a roster match.)
   - Click Deploy and copy the **Web app URL** (ends in `/exec`).
7. Put that URL into `rsvp/index.html` — the empty `content=""` in:
   `<meta name="rsvp-endpoint" content="">` — commit and push.
   (Until the URL is in place, the page falls back to a pre-filled email
   RSVP, so nothing is ever broken.)

## Test before invites go out

- Submit the form with a roster name + your own email → venue should appear
  on screen and the confirmation email (with .ics attached) should arrive.
- Submit with a made-up name → "we'll email you the details" (no venue), and
  the row shows **no match**.
- Submit a regrets RSVP → thanks screen, no venue.
- Check all three rows landed in the Sheet with the right photo-permission
  values.

## Editing the script later

Use **Deploy → Manage deployments → ✏️ edit → Version: New version → Deploy**.
That keeps the SAME `/exec` URL. ("New deployment" would mint a different URL
and the site would need a commit.)

## After the party

- Filter the `RSVPs` tab on `Photo permission = YES` → that's the
  photographer's cleared list (export it for them before the event).
- The Sheet is the consent record — keep it until the photo album is settled,
  then archive/delete per the privacy page.
