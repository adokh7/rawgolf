const { google } = require('googleapis');
const path = require('path');
const keys = require(path.join(__dirname, 'service_account.json'));

const urlToIndex = process.argv[2];

if (!urlToIndex) {
  console.error('⚠️ Usage: node index-now.js <CANONICAL_URL>');
  process.exit(1);
}

const client = new google.auth.JWT(
  keys.client_email,
  null,
  keys.private_key,
  ['https://www.googleapis.com/auth/indexing'],
  null
);

client.authorize((err) => {
  if (err) {
    console.error('❌ Authentication failed:', err.message);
    return;
  }

  google.indexing('v3').urlNotifications.publish({
    auth: client,
    requestBody: {
      url: urlToIndex,
      type: 'URL_UPDATED'
    }
  }, (err, res) => {
    if (err) {
      console.error('❌ Indexing request failed:', err.message);
    } else {
      console.log('✅ Google Indexing API Success!');
      console.log('🔗 Instant indexed URL:', urlToIndex);
    }
  });
});
