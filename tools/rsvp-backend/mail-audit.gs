/**
 * MAIL AUDIT — paste at the BOTTOM of Code.gs, then run `checkMail`.
 * Read-only: sends nothing, changes nothing, needs NO redeployment.
 * Results appear in the editor's Execution log.
 */
function checkMail() {
  var quota = MailApp.getRemainingDailyQuota();
  var sheet = SpreadsheetApp.getActive().getSheetByName('RSVPs');
  var rows = sheet.getLastRow() - 1;
  var attending = 0, yes = 0, no = 0;

  if (rows > 0) {
    var data = sheet.getRange(2, 5, rows, 2).getValues(); // columns E and F
    for (var i = 0; i < data.length; i++) {
      if (String(data[i][0]).toLowerCase() === 'yes') {
        attending++;
        if (String(data[i][1]).toUpperCase() === 'YES') yes++; else no++;
      }
    }
  }

  Logger.log('=== BECOMING PARTY — MAIL & RSVP CHECK ===');
  Logger.log('Emails left to send today: ' + quota);
  Logger.log('  covers about ' + Math.floor(quota / 2) + ' more attending RSVPs');
  Logger.log(quota < 10 ? '  *** LOW — confirmations may start failing silently ***'
                        : '  plenty of room');
  Logger.log('---');
  Logger.log('RSVP rows in sheet: ' + rows);
  Logger.log('Attending families: ' + attending);
  Logger.log('  photo permission YES: ' + yes);
  Logger.log('  photo permission NO:  ' + no);
  Logger.log('---');
  Logger.log('Reminder: script email never appears in Gmail Sent, so the only');
  Logger.log('proof a parent received the address is asking them.');
}
