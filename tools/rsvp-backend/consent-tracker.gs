/**
 * PHOTO CONSENT TRACKER — paste this at the BOTTOM of the existing Code.gs
 * (do NOT replace the file: that would wipe your CONFIG venue values).
 *
 * Then run `installConsentTracking` once from the editor's function dropdown.
 * Running a function in the editor does NOT require redeploying the web app —
 * the /exec URL and everything already live stay exactly as they are.
 *
 * What it does:
 *  1. Colors the "Photo permission" column on the RSVPs tab — green YES,
 *     amber NO — so consent is readable at a glance.
 *  2. Widens the columns so nothing hides off-screen.
 *  3. Creates a "PHOTO CONSENT" tab: live counts, a CLEARED list (the
 *     photographer's list), and a DO NOT PUBLISH list. Both update
 *     themselves as RSVPs arrive — including rows you type in by hand for
 *     families who RSVP'd by email or in person.
 */

function installConsentTracking() {
  var ss = SpreadsheetApp.getActive();
  var rsvps = ss.getSheetByName('RSVPs');
  if (!rsvps) throw new Error('No RSVPs tab found — run setup() first.');

  // — 1. make the consent column obvious —
  var col = rsvps.getRange('F2:F1000');
  var yes = SpreadsheetApp.newConditionalFormatRule()
    .whenTextEqualTo('YES')
    .setBackground('#d9ead3').setFontColor('#1e4620').setBold(true)
    .setRanges([col]).build();
  var no = SpreadsheetApp.newConditionalFormatRule()
    .whenTextEqualTo('NO')
    .setBackground('#fce5cd').setFontColor('#7f4b12').setBold(true)
    .setRanges([col]).build();
  rsvps.setConditionalFormatRules([yes, no]);

  rsvps.getRange('A1:H1').setBackground('#f6ded6').setFontWeight('bold');
  var widths = [150, 190, 230, 220, 90, 150, 130, 260];
  for (var i = 0; i < widths.length; i++) rsvps.setColumnWidth(i + 1, widths[i]);
  rsvps.setFrozenRows(1);

  // — 2. the live consent tab —
  var t = ss.getSheetByName('PHOTO CONSENT') || ss.insertSheet('PHOTO CONSENT');
  t.clear();
  t.getRange('A1').setValue('PHOTO & VIDEO CONSENT — live from the RSVPs tab')
    .setFontSize(14).setFontWeight('bold');
  t.getRange('A2').setValue('Updates itself as RSVPs arrive. Add email/phone RSVPs as rows on the RSVPs tab (put YES or NO in column F) and they appear here too.')
    .setFontColor('#666666');

  t.getRange('A4').setValue('Cleared to publish (families)').setFontWeight('bold');
  t.getRange('B4').setFormula('=COUNTIFS(RSVPs!F2:F,"YES",RSVPs!E2:E,"yes")');
  t.getRange('A5').setValue('Do NOT publish (families)').setFontWeight('bold');
  t.getRange('B5').setFormula('=COUNTIFS(RSVPs!F2:F,"NO",RSVPs!E2:E,"yes")');
  t.getRange('A6').setValue('Attending families total').setFontWeight('bold');
  t.getRange('B6').setFormula('=COUNTIF(RSVPs!E2:E,"yes")');
  t.getRange('A7').setValue('Headcount (kids + adults)').setFontWeight('bold');
  t.getRange('B7').setFormula('=SUMIF(RSVPs!E2:E,"yes",RSVPs!G2:G)');

  t.getRange('A9').setValue('✓ CLEARED — photographer may publish these children')
    .setFontWeight('bold').setBackground('#d9ead3');
  t.getRange('A10').setValue('Child(ren)').setFontWeight('bold');
  t.getRange('B10').setValue('Parent/guardian').setFontWeight('bold');
  t.getRange('A11').setFormula(
    '=IFERROR(FILTER({RSVPs!D2:D,RSVPs!B2:B},RSVPs!F2:F="YES",RSVPs!E2:E="yes"),"— none yet —")');

  t.getRange('E9').setValue('✕ DO NOT PUBLISH — keep out of anything public')
    .setFontWeight('bold').setBackground('#fce5cd');
  t.getRange('E10').setValue('Child(ren)').setFontWeight('bold');
  t.getRange('F10').setValue('Parent/guardian').setFontWeight('bold');
  t.getRange('E11').setFormula(
    '=IFERROR(FILTER({RSVPs!D2:D,RSVPs!B2:B},RSVPs!F2:F="NO",RSVPs!E2:E="yes"),"— none yet —")');

  [1, 2, 5, 6].forEach(function (c) { t.setColumnWidth(c, 240); });
  t.setColumnWidth(3, 40); t.setColumnWidth(4, 40);
  ss.setActiveSheet(t);
}
