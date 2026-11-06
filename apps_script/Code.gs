/**
 * Pitch Evaluation Study: Google Sheet backend.
 *
 * Paste this into Extensions > Apps Script of an empty Google Sheet, then
 * Deploy > New deployment > Web app, Execute as: Me, Who has access: Anyone.
 * Copy the web app URL into the Streamlit app's secrets as SHEET_URL (see experiment/README.md).
 *
 * Tabs it creates:
 *   responses    one row per participant per pitch (3 rows per participant)
 *   raw          the full JSON record per participant, as a backup
 *   bonus        bonus-draw contacts, with no participant id (cannot be linked)
 */

// Only needed if this script was NOT opened from the Sheet (Extensions > Apps Script):
// paste the Sheet's id here (the long part of its URL between /d/ and /edit).
var SHEET_ID = '';

function book_() {
  return SpreadsheetApp.getActiveSpreadsheet() || SpreadsheetApp.openById(SHEET_ID);
}

function sheet_(name, header) {
  var ss = book_();
  var sh = ss.getSheetByName(name) || ss.insertSheet(name);
  if (header && sh.getLastRow() === 0) sh.appendRow(header);
  return sh;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  return json_({ ok: true });
}

/** POST body (sent as text): {type:"response", columns, rows, raw} or {type:"bonus", contact, at}. */
function doPost(e) {
  var body = JSON.parse(e.postData.contents);
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    if (body.type === 'response') {
      var sh = sheet_('responses', body.columns);
      body.rows.forEach(function (r) { sh.appendRow(r); });
      sheet_('raw', ['received_at', 'participant_id', 'json']).appendRow([new Date(), body.raw && body.raw.pid, JSON.stringify(body.raw)]);
      return json_({ ok: true });
    }
    if (body.type === 'bonus') {
      sheet_('bonus', ['received_at', 'contact']).appendRow([new Date(), String(body.contact || '').slice(0, 200)]);
      return json_({ ok: true });
    }
    return json_({ ok: false, error: 'unknown type' });
  } finally {
    lock.releaseLock();
  }
}
