/**
 * MAIL AUDIT — paste at the BOTTOM of Code.gs (never replace the file:
 * that wipes your CONFIG venue values). Run `checkMail` from the editor's
 * function dropdown. Read-only: it sends nothing, changes nothing, and
 * needs NO redeployment — the live /exec URL is untouched.
 *
 * Why: every attending RSVP sends TWO emails (the parent's confirmation
 * with the address, plus your notify copy). A consumer Gmail account
 * allows 100 recipients/day for scripts. If that ceiling is hit, the
 * parent's confirmation fails SILENTLY — the RSVP still lands in the
 * sheet and you still get told "venue sent automatically", but that
 * family never received the address.
 */

function checkMail() {
  var quota = MailApp.getRemainingDailyQuota();
  var sheet = SpreadsheetApp.getActive().getSheetByName('RSVPs');
  var rows = sheet.getLastRow() - 1;
  var attending = 0, cleared = 0, declined = 0;

  if (rows > 0) {
    var data = sheet.getRange(2, 5, rows, 2).getValues(); // cols E, F
    for (var i = 0; i < data.length; i++) {
      if (String(data[i][0]).toLowerCase() === 'yes') {
        attending++;
        if (String(data[i][1]).toUpperCase() === 'YES') cleared++; else declined++;
      }
    }
  }

  var msg =
    'MAIL QUOTA REMAINING TODAY: ' + quota + ' recipients\n' +
    '  → covers about ' + Math.floor(quota / 2) + ' more attending RSVPs\n' +
    (quota < 10 ? '  ⚠ LOW — confirmations may start failing silently.\n' : '') +
    '\nSHEET TOTALS\n' +
    '  RSVP rows: ' + rows + '\n' +
    '  Attending families: ' + attending + '\n' +
    '  Photo permission YES: ' + cleared + '\n' +
    '  Photo permission NO: ' + declined + '\n' +
    '\nNote: script-sent mail does NOT appear in Gmail’s Sent folder,\n' +
    'so the only proof a parent got the address is asking them.';

  Logger.log(msg);
  try { SpreadsheetApp.getUi().alert(msg); } catch (e) {}
  return msg;
}
