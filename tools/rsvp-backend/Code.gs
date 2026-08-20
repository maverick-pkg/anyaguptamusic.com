/**
 * Becoming Pre-Launch Party — RSVP + photo-permission backend.
 *
 * Paste this into an Apps Script project BOUND to a private Google Sheet
 * (Sheet → Extensions → Apps Script). See DEPLOY.md next to this file.
 *
 * POLICY (user ruling 2026-08-19): every attending RSVP gets the venue
 * automatically — on screen and by confirmation email. No guest-roster
 * gate. Every submission is recorded and a notify email goes out per
 * RSVP, so the Sheet is the door list and odd entries are visible.
 *
 * PRIVACY RULES (this repo is public):
 *  - The real venue name/address is pasted ONLY here, at deploy time,
 *    inside your private Apps Script project. Never commit it to the repo.
 */

var CONFIG = {
  VENUE_NAME: 'PASTE VENUE NAME AT DEPLOY',          // e.g. the venue's name
  VENUE_ADDRESS: 'PASTE STREET ADDRESS AT DEPLOY',   // street, city, state zip
  EVENT_TITLE: 'Becoming Pre-Launch Party — Anya Gupta',
  WHEN_TEXT: 'Saturday, September 12, 2026 · 6:00–9:00 PM',
  START_UTC: '20260912T230000Z', // 6:00 PM CDT
  END_UTC:   '20260913T020000Z', // 9:00 PM CDT
  FROM_NAME: 'Anya Gupta',
  REPLY_TO: 'email@anyaguptamusic.com',
  NOTIFY: ''  // your own inbox for a heads-up per RSVP; '' = Sheet only
};

var HEADERS = ['Timestamp', 'Parent/guardian', 'Email', 'Child(ren)',
  'Attending', 'Photo permission', 'Total attending', 'Note'];

/** One-time: run this from the editor to create/repair the RSVPs tab.
 *  Safe to re-run; it only rewrites the header row. A leftover GuestList
 *  tab from the earlier roster-gated version can simply be deleted. */
function setup() {
  var ss = SpreadsheetApp.getActive();
  var rsvps = ss.getSheetByName('RSVPs') || ss.insertSheet('RSVPs');
  rsvps.getRange('1:1').clearContent();
  rsvps.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
  rsvps.setFrozenRows(1);
}

function doPost(e) {
  try {
    var p = (e && e.parameter) || {};
    if (p.website) return json_({ ok: true }); // honeypot: pretend success

    var parent = clip_(p.parent), email = clip_(p.email),
        children = clip_(p.children), note = clip_(p.note),
        count = clip_(p.count);
    var attending = p.attending === 'yes';
    var mediaYes = p.media === 'yes';
    if (!parent || !email || !children) return json_({ ok: false });

    var ss = SpreadsheetApp.getActive();
    ss.getSheetByName('RSVPs').appendRow([
      new Date(), parent, email, children,
      attending ? 'yes' : 'no', mediaYes ? 'YES' : 'NO', count, note
    ]);

    // Refuse to reveal placeholder config — behaves as "we'll email you".
    var configured = CONFIG.VENUE_ADDRESS.indexOf('PASTE') < 0;

    if (attending && configured) {
      try { sendConfirmation_(parent, email, children, mediaYes); } catch (err) {}
    }
    notifySelf_(parent, email, children, attending, mediaYes, count, note);

    var out = { ok: true, attending: attending };
    if (attending && configured) {
      out.matched = true; // page contract: matched + address => show venue
      out.venue = CONFIG.VENUE_NAME;
      out.address = CONFIG.VENUE_ADDRESS;
      out.map = 'https://maps.google.com/?q=' +
        encodeURIComponent(CONFIG.VENUE_NAME + ', ' + CONFIG.VENUE_ADDRESS);
      out.gcal = gcalUrl_();
    }
    return json_(out);
  } catch (err) {
    return json_({ ok: false });
  }
}

// ——— helpers ———

function clip_(v) { return String(v || '').trim().slice(0, 500); }

function gcalUrl_() {
  return 'https://calendar.google.com/calendar/render?action=TEMPLATE' +
    '&text=' + encodeURIComponent(CONFIG.EVENT_TITLE) +
    '&dates=' + CONFIG.START_UTC + '/' + CONFIG.END_UTC +
    '&location=' + encodeURIComponent(CONFIG.VENUE_NAME + ', ' + CONFIG.VENUE_ADDRESS) +
    '&details=' + encodeURIComponent('Private event — see your RSVP confirmation email.');
}

function ics_() {
  return ['BEGIN:VCALENDAR', 'VERSION:2.0',
    'PRODID:-//Anya Gupta//Becoming Party//EN', 'BEGIN:VEVENT',
    'UID:becoming-party-2026@anyaguptamusic.com',
    'DTSTAMP:' + Utilities.formatDate(new Date(), 'UTC', "yyyyMMdd'T'HHmmss'Z'"),
    'DTSTART:' + CONFIG.START_UTC, 'DTEND:' + CONFIG.END_UTC,
    'SUMMARY:' + CONFIG.EVENT_TITLE,
    'LOCATION:' + CONFIG.VENUE_NAME + '\\, ' + CONFIG.VENUE_ADDRESS.replace(/,/g, '\\,'),
    'DESCRIPTION:Private event — please don\'t share the location publicly.',
    'END:VEVENT', 'END:VCALENDAR'].join('\r\n');
}

function sendConfirmation_(parent, email, children, mediaYes) {
  var mediaLine = mediaYes
    ? 'Photo & video permission: GRANTED — thank you! Photos or video that include your child may appear on anyaguptamusic.com, Anya\'s social media, and press materials about her music. Names are never published. Change your mind anytime: just reply to this email.'
    : 'Photo & video permission: DECLINED — noted with zero hard feelings. Our photographer will keep your child out of anything we publish.';
  var body =
    'Hi ' + parent + ',\n\n' +
    'You\'re confirmed for the Becoming pre-launch party!\n\n' +
    'Who: ' + children + ' (and you!)\n' +
    'When: ' + CONFIG.WHEN_TEXT + '\n' +
    'Where: ' + CONFIG.VENUE_NAME + '\n' +
    '       ' + CONFIG.VENUE_ADDRESS + '\n\n' +
    'Add to calendar: ' + gcalUrl_() + '\n' +
    '(An invite file is also attached for Apple/Outlook calendars.)\n\n' +
    mediaLine + '\n\n' +
    'Private event — please don\'t share the location publicly.\n\n' +
    'See you there ✦\nAnya & family';
  MailApp.sendEmail({
    to: email,
    subject: 'You\'re confirmed ✦ Becoming Pre-Launch Party — Sep 12',
    body: body,
    name: CONFIG.FROM_NAME,
    replyTo: CONFIG.REPLY_TO,
    attachments: [Utilities.newBlob(ics_(), 'text/calendar', 'becoming-party.ics')]
  });
}

function notifySelf_(parent, email, children, attending, mediaYes, count, note) {
  if (!CONFIG.NOTIFY) return;
  var flag = attending ? 'Confirmed' : 'Regrets';
  try {
    MailApp.sendEmail({
      to: CONFIG.NOTIFY,
      subject: 'RSVP [' + flag + '] ' + parent + ' — ' + children,
      body: 'Parent: ' + parent + '\nEmail: ' + email + '\nChild(ren): ' + children +
        '\nAttending: ' + (attending ? 'yes — venue sent automatically' : 'no') +
        '\nPhoto permission: ' + (mediaYes ? 'YES' : 'NO') +
        '\nTotal attending: ' + (count || '—') + '\nNote: ' + (note || '—') +
        '\n\nFull list: ' + SpreadsheetApp.getActive().getUrl()
    });
  } catch (err) {}
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
