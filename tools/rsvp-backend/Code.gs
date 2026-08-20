/**
 * Becoming Pre-Launch Party — RSVP + photo-permission backend.
 *
 * Paste this into an Apps Script project BOUND to a private Google Sheet
 * (Sheet → Extensions → Apps Script). See DEPLOY.md next to this file.
 *
 * PRIVACY RULES (this repo is public):
 *  - The real venue name/address is pasted ONLY here, at deploy time,
 *    inside your private Apps Script project. Never commit it to the repo.
 *  - The guest roster lives ONLY in the private Sheet's "GuestList" tab.
 *    Never commit guest names to the repo.
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

/** One-time: run this from the editor to create the tabs, then authorize. */
function setup() {
  var ss = SpreadsheetApp.getActive();
  var rsvps = ss.getSheetByName('RSVPs') || ss.insertSheet('RSVPs');
  if (rsvps.getLastRow() === 0) {
    rsvps.appendRow(['Timestamp', 'Parent/guardian', 'Email', 'Child(ren)',
      'Attending', 'Photo permission', 'Total attending', 'Note', 'Roster match']);
    rsvps.setFrozenRows(1);
  }
  var roster = ss.getSheetByName('GuestList') || ss.insertSheet('GuestList');
  if (roster.getLastRow() === 0) {
    roster.appendRow(['Invited child — first & last name (one per row)']);
    roster.appendRow(['Ava Example']);   // ← replace these two sample rows
    roster.appendRow(['Liam Sample']);   //   with the real roster (Sheet only!)
    roster.setFrozenRows(1);
  }
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
    var matched = matchRoster_(children, ss);

    ss.getSheetByName('RSVPs').appendRow([
      new Date(), parent, email, children,
      attending ? 'yes' : 'no', mediaYes ? 'YES' : 'NO',
      count, note, matched ? 'MATCH' : 'no match'
    ]);

    if (attending && matched) {
      try { sendConfirmation_(parent, email, children, mediaYes); } catch (err) {}
    }
    notifySelf_(parent, email, children, attending, mediaYes, count, note, matched);

    var out = { ok: true, matched: matched, attending: attending };
    if (attending && matched) {
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

function norm_(s) {
  return String(s || '').toLowerCase()
    .replace(/[^a-zÀ-ɏ' -]/g, ' ')
    .replace(/\s+/g, ' ').trim();
}

/** True if ANY submitted child matches the GuestList roster. */
function matchRoster_(children, ss) {
  var sheet = ss.getSheetByName('GuestList');
  if (!sheet || sheet.getLastRow() < 2) return false;
  var roster = sheet.getRange(2, 1, sheet.getLastRow() - 1, 1).getValues()
    .map(function (r) { return norm_(r[0]); })
    .filter(function (s) { return s && s.indexOf('example') < 0 && s.indexOf('sample') < 0; });
  if (!roster.length) return false;

  var firstCounts = {};
  roster.forEach(function (full) {
    var f = full.split(' ')[0];
    firstCounts[f] = (firstCounts[f] || 0) + 1;
  });

  var submitted = String(children).split(/,|&| and /i)
    .map(norm_).filter(function (s) { return s; });

  return submitted.some(function (kid) {
    if (roster.indexOf(kid) >= 0) return true;              // exact full-name match
    var first = kid.split(' ')[0];                           // unique-first-name match
    return firstCounts[first] === 1 && roster.some(function (full) {
      return full.split(' ')[0] === first;
    });
  });
}

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

function notifySelf_(parent, email, children, attending, mediaYes, count, note, matched) {
  if (!CONFIG.NOTIFY) return;
  var flag = !attending ? 'Regrets' : (matched ? 'Confirmed' : 'NEEDS MANUAL REPLY');
  try {
    MailApp.sendEmail({
      to: CONFIG.NOTIFY,
      subject: 'RSVP [' + flag + '] ' + parent + ' — ' + children,
      body: 'Parent: ' + parent + '\nEmail: ' + email + '\nChild(ren): ' + children +
        '\nAttending: ' + (attending ? 'yes' : 'no') +
        '\nPhoto permission: ' + (mediaYes ? 'YES' : 'NO') +
        '\nTotal attending: ' + (count || '—') + '\nNote: ' + (note || '—') +
        '\nRoster match: ' + (matched ? 'yes — venue sent automatically' :
          'NO — nothing sent; reply manually if they\'re legit') +
        '\n\nFull list: ' + SpreadsheetApp.getActive().getUrl()
    });
  } catch (err) {}
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
