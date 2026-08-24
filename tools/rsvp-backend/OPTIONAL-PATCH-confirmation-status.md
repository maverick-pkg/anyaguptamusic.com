# Optional patch — stop trusting "venue sent automatically"

**Problem.** `doPost` sends the parent's confirmation inside a `try` with an
empty `catch`, so a failed send is swallowed. The notify email then reports
`Attending: yes — venue sent automatically` whether or not it actually went.
Combined with the fact that script-sent mail never appears in Gmail's Sent
folder, a family can silently end up without the address.

**Risk note.** The form is live and taking real RSVPs. This edit touches
`doPost`, so it needs a redeploy (Deploy → Manage deployments → ✏️ → Version:
**New version** → Deploy — same `/exec` URL). Only do it if you want the
extra visibility; the read-only `checkMail()` in `mail-audit.gs` gives you
most of the safety with zero risk.

## Edit 1 — in `doPost`, replace these four lines

```js
    if (attending && configured) {
      try { sendConfirmation_(parent, email, children, mediaYes); } catch (err) {}
    }
    notifySelf_(parent, email, children, attending, mediaYes, count, note);
```

with

```js
    var sent = attending ? (configured ? 'pending' : 'no venue configured')
                         : 'n/a (regrets)';
    if (attending && configured) {
      try { sendConfirmation_(parent, email, children, mediaYes); sent = 'sent'; }
      catch (err) { sent = 'FAILED — send the address by hand: ' + err; }
    }
    try { sheet.getRange(sheet.getLastRow(), 9).setValue(sent); } catch (e) {}
    notifySelf_(parent, email, children, attending, mediaYes, count, note, sent);
```

## Edit 2 — a few lines above, give the sheet a name

Replace

```js
    ss.getSheetByName('RSVPs').appendRow([
```

with

```js
    var sheet = ss.getSheetByName('RSVPs');
    sheet.appendRow([
```

## Edit 3 — in `notifySelf_`, accept and print the real status

Replace the function's first line

```js
function notifySelf_(parent, email, children, attending, mediaYes, count, note) {
```

with

```js
function notifySelf_(parent, email, children, attending, mediaYes, count, note, sent) {
```

and replace

```js
        '\nAttending: ' + (attending ? 'yes — venue sent automatically' : 'no') +
```

with

```js
        '\nAttending: ' + (attending ? 'yes' : 'no') +
        '\nConfirmation email: ' + (sent || 'unknown') +
```

## Edit 4 — add the header (optional)

In `HEADERS`, append `'Confirmation'` so column I is labelled, then run
`setup()` once. Existing rows are untouched; the consent tracker's formulas
(columns B, D, E, F, G) are unaffected.
