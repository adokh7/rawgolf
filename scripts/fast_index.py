#!/usr/bin/env python3
"""Notify discovery services after new or changed content is deployed.

  python3 scripts/fast_index.py                 # ping WebSub + submit changed URLs
  python3 scripts/fast_index.py --websub        # WebSub hub ping only
  python3 scripts/fast_index.py --indexnow URL… # submit specific URLs
  python3 scripts/fast_index.py --dry-run       # show what would be sent

The default channels are deliberately limited to services that support normal
editorial pages:

  WebSub (PubSubHubbub) — publisher pings a hub, the hub fetches feed.xml and
  fans it out to subscribers. This distributes the feed; it is not a Google
  Search indexing request.

  IndexNow — a direct submit API shared by Bing, Yandex, Seznam and Naver.
  Google has publicly said it does NOT use IndexNow. Google discovers ordinary
  news and guide pages through crawlable internal links and sitemap.xml.

Google's Indexing API is only used when a queued page actually contains
JobPosting schema or a VideoObject with an embedded BroadcastEvent. Sending a
NewsArticle to that API can return HTTP 200 for notification receipt while the
URL remains ineligible for the API and unindexed.

Stdlib only: this runs in CI and on a bare machine with no pip install.
"""
import sys, os, json, ssl, re, html
import urllib.request, urllib.parse, urllib.error


def _ssl_context():
    """Build a verifying SSL context that works on installs with no CA bundle.

    A stock python.org install on macOS ships no root certificates until
    `Install Certificates.command` is run, so urllib fails every HTTPS request
    with CERTIFICATE_VERIFY_FAILED while curl (system trust store) succeeds.
    Fall back to certifi's bundle. Verification stays ON either way — a
    fast-indexing helper is not a reason to disable TLS checks.
    """
    paths = ssl.get_default_verify_paths()
    if paths.cafile or paths.capath:
        return ssl.create_default_context()
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


SSL_CTX = _ssl_context()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.golfraw.com'
FEED_URL = SITE + '/feed.xml'

WEBSUB_HUBS = [
    'https://pubsubhubbub.appspot.com/',
    'https://pubsubhubbub.superfeedr.com/',
]

INDEXNOW_ENDPOINT = 'https://api.indexnow.org/indexnow'
INDEXNOW_KEY = '2b40e02668c858091ec0b87f33500435'
INDEXNOW_KEY_LOCATION = f'{SITE}/{INDEXNOW_KEY}.txt'

# IndexNow rejects batches over 10,000 URLs.
INDEXNOW_MAX = 10000

TIMEOUT = 20
UA = 'golfraw-fast-index/1.0 (+https://www.golfraw.com/)'


def normalize_urls(urls, verbose=False):
    """Return unique, canonical production URLs and reject malformed input.

    Queue files are local state and should already contain clean paths, but a
    defensive normalizer prevents accidental ``.html`` URLs, query strings,
    fragments, brackets, foreign hosts, or trailing-slash duplicates from
    reaching IndexNow or Google.
    """
    accepted, rejected = [], []
    for raw in urls or []:
        value = str(raw or '').strip()
        if not value:
            rejected.append((raw, 'empty URL'))
            continue
        if value.startswith('http://') or value.startswith('https://'):
            parts = urllib.parse.urlsplit(value)
            if parts.scheme != 'https' or parts.netloc.lower() != 'www.golfraw.com':
                rejected.append((raw, 'URL must use https://www.golfraw.com'))
                continue
        else:
            if not value.startswith('/'):
                value = '/' + value
            parts = urllib.parse.urlsplit(SITE + value)
        if parts.query or parts.fragment:
            rejected.append((raw, 'query strings and fragments are not canonical'))
            continue
        path = parts.path or '/'
        decoded = urllib.parse.unquote(path)
        if any(c in decoded for c in '[]\\') or re.search(r'\s', decoded):
            rejected.append((raw, 'brackets, backslashes, and whitespace are invalid'))
            continue
        if path.endswith('.html'):
            path = path[:-5]
        if path != '/':
            path = path.rstrip('/')
        if not path.startswith('/') or '//' in path:
            rejected.append((raw, 'invalid path'))
            continue
        accepted.append(SITE + path)
    accepted = list(dict.fromkeys(accepted))
    if verbose:
        for raw, reason in rejected:
            print(f'  REJECT URL {raw!r}: {reason}')
    return accepted, rejected


def _post(url, data, headers, timeout=TIMEOUT):
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
            return r.status, r.read(400).decode('utf-8', 'replace').strip()
    except urllib.error.HTTPError as e:
        return e.code, e.read(400).decode('utf-8', 'replace').strip()
    except Exception as e:                      # DNS, TLS, timeout, offline
        return None, f'{type(e).__name__}: {e}'


def ping_websub(feed_url=FEED_URL, hubs=None, dry_run=False, verbose=True):
    """Tell each hub that feed_url has new content.

    A hub answers 204 (or 202) on success, then fetches the feed itself. It
    will only accept the ping if the feed advertises that hub via
    <atom:link rel="hub">, which write_feed() in sync_site.py emits.
    """
    hubs = hubs or WEBSUB_HUBS
    body = urllib.parse.urlencode({'hub.mode': 'publish', 'hub.url': feed_url}).encode()
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': UA}
    results = []
    for hub in hubs:
        if dry_run:
            if verbose:
                print(f'  [dry-run] POST {hub} hub.mode=publish hub.url={feed_url}')
            results.append((hub, None, 'dry-run'))
            continue
        status, body_text = _post(hub, body, headers)
        ok = status in (200, 202, 204)
        if verbose:
            mark = 'ok  ' if ok else 'FAIL'
            print(f'  {mark} WebSub {hub} -> {status or "no response"} {body_text[:90]}')
        results.append((hub, status, body_text))
    return results


def submit_indexnow(urls, key=INDEXNOW_KEY, dry_run=False, verbose=True):
    """Submit changed URLs to the IndexNow API.

    Ownership is proven by hosting <key>.txt at the site root; the endpoint
    fetches it before accepting the batch, so that file must be deployed
    BEFORE the first submission or everything returns 403.
    """
    urls, rejected = normalize_urls(urls, verbose=verbose)
    if rejected:
        return 400, f'{len(rejected)} invalid URL(s) rejected before submission'
    if not urls:
        if verbose:
            print('  IndexNow: nothing to submit')
        return None, 'no urls'
    if len(urls) > INDEXNOW_MAX:
        if verbose:
            print(f'  IndexNow: trimming {len(urls)} urls to {INDEXNOW_MAX}')
        urls = urls[:INDEXNOW_MAX]

    payload = {
        'host': 'www.golfraw.com',
        'key': key,
        'keyLocation': INDEXNOW_KEY_LOCATION,
        'urlList': urls,
    }
    if dry_run:
        if verbose:
            print(f'  [dry-run] POST {INDEXNOW_ENDPOINT} with {len(urls)} url(s)')
            for u in urls[:5]:
                print(f'      {u}')
            if len(urls) > 5:
                print(f'      ... +{len(urls)-5} more')
        return None, 'dry-run'

    status, body_text = _post(
        INDEXNOW_ENDPOINT, json.dumps(payload).encode(),
        {'Content-Type': 'application/json; charset=utf-8', 'User-Agent': UA})
    if verbose:
        # 200 accepted, 202 accepted-pending-key-validation
        mark = 'ok  ' if status in (200, 202) else 'FAIL'
        print(f'  {mark} IndexNow {len(urls)} url(s) -> {status or "no response"} '
              f'{body_text[:90]}')
    return status, body_text


def pending_urls():
    """URLs recorded by the last sync as new or changed."""
    p = os.path.join(ROOT, '.fast-index-pending.json')
    if not os.path.exists(p):
        return []
    try:
        return json.load(open(p, encoding='utf-8')).get('urls', [])
    except (ValueError, OSError):
        return []


def _schema_types(value):
    """Yield Schema.org @type values recursively from decoded JSON-LD."""
    if isinstance(value, dict):
        kind = value.get('@type')
        if isinstance(kind, str):
            yield kind
        elif isinstance(kind, list):
            yield from (item for item in kind if isinstance(item, str))
        for child in value.values():
            yield from _schema_types(child)
    elif isinstance(value, list):
        for child in value:
            yield from _schema_types(child)


def _has_embedded_broadcast_event(value):
    if isinstance(value, dict):
        kinds = value.get('@type', [])
        if isinstance(kinds, str):
            kinds = [kinds]
        if 'VideoObject' in kinds:
            nested = set()
            for child in value.values():
                nested.update(_schema_types(child))
            if 'BroadcastEvent' in nested:
                return True
        return any(_has_embedded_broadcast_event(child) for child in value.values())
    if isinstance(value, list):
        return any(_has_embedded_broadcast_event(child) for child in value)
    return False


def google_indexing_eligible(url):
    """Whether a local page is eligible for Google's restricted Indexing API."""
    normalized, rejected = normalize_urls([url])
    if rejected or not normalized:
        return False
    path = urllib.parse.urlsplit(normalized[0]).path
    local = os.path.join(ROOT, 'index.html' if path == '/' else path.lstrip('/') + '.html')
    try:
        source = open(local, encoding='utf-8').read()
    except OSError:
        return False
    scripts = re.findall(
        r'<script\b[^>]*\btype=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        source, flags=re.I | re.S)
    for raw in scripts:
        try:
            data = json.loads(html.unescape(raw).strip())
        except (ValueError, TypeError):
            continue
        if 'JobPosting' in set(_schema_types(data)) or _has_embedded_broadcast_event(data):
            return True
    return False


def notify_google(urls, dry_run=False, verbose=True):
    """Notify Google only for pages covered by the Indexing API policy.

    A successful HTTP response means Google accepted the notification. It is
    not proof that a page was crawled, indexed, or eligible to rank.
    """
    urls, rejected = normalize_urls(urls, verbose=verbose)
    if rejected:
        return False
    eligible = [url for url in urls if google_indexing_eligible(url)]
    skipped = len(urls) - len(eligible)
    if skipped and verbose:
        print(f'  Google Indexing API: SKIP {skipped} ineligible editorial URL(s); '
              'use sitemap.xml and internal links')
    urls = eligible
    if not urls:
        return True

    key_path = os.path.join(ROOT, 'service_account.json')
    if not os.path.exists(key_path):
        if verbose:
            print(f'  Google Indexing: SKIP - {key_path} not found')
        return False

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        credentials = service_account.Credentials.from_service_account_file(
            key_path, scopes=['https://www.googleapis.com/auth/indexing']
        )
        service = build('indexing', 'v3', credentials=credentials)
    except ImportError:
        if verbose:
            print('  Google Indexing: SKIP - google-api-python-client not installed')
        return False
    except Exception as e:
        if verbose:
            print(f'  Google Indexing: INIT FAIL - {e}')
        return False

    ok = True
    for url in urls:
        if dry_run:
            if verbose:
                print(f'  [dry-run] Google Indexing: URL_UPDATED {url}')
            continue
        try:
            body = {
                'url': url,
                'type': 'URL_UPDATED'
            }
            response = service.urlNotifications().publish(body=body).execute()
            if verbose:
                metadata = response.get('urlNotificationMetadata', {}) if isinstance(response, dict) else {}
                update = metadata.get('latestUpdate', {}) if isinstance(metadata, dict) else {}
                stamp = update.get('notifyTime', '') if isinstance(update, dict) else ''
                suffix = f' notifyTime={stamp}' if stamp else ''
                print(f'  ok   Google Indexing API notification {url} -> 200 OK{suffix}')
        except Exception as e:
            ok = False
            if verbose:
                print(f'  FAIL Google Indexing {url} -> {e}')
    return ok


def clear_pending():
    p = os.path.join(ROOT, '.fast-index-pending.json')
    if os.path.exists(p):
        os.remove(p)


def notify(urls=None, dry_run=False, verbose=True):
    """Fire all applicable channels and retain the queue on any failure."""
    from_pending = urls is None
    urls = pending_urls() if from_pending else urls
    urls, rejected = normalize_urls(urls, verbose=verbose)
    if verbose:
        print(f'fast-index: {len(urls)} changed URL(s)')
    websub = ping_websub(dry_run=dry_run, verbose=verbose)
    index_status, _ = submit_indexnow(urls, dry_run=dry_run, verbose=verbose)
    google_ok = notify_google(urls, dry_run=dry_run, verbose=verbose)
    websub_ok = dry_run or all(status in (200, 202, 204) for _, status, _ in websub)
    indexnow_ok = dry_run or not urls or index_status in (200, 202)
    success = not rejected and websub_ok and indexnow_ok and google_ok
    if not dry_run and from_pending and os.path.exists(os.path.join(ROOT, '.fast-index-pending.json')):
        if success:
            clear_pending()
            if verbose:
                print('  queue: cleared after successful delivery')
        elif verbose:
            print('  queue: RETAINED because at least one delivery failed')
    return success


if __name__ == '__main__':
    args = sys.argv[1:]
    dry = '--dry-run' in args
    args = [a for a in args if a != '--dry-run']
    if args and args[0] == '--websub':
        results = ping_websub(dry_run=dry)
        success = dry or all(status in (200, 202, 204) for _, status, _ in results)
    elif args and args[0] == '--indexnow':
        urls = args[1:] or pending_urls()
        status, _ = submit_indexnow(urls, dry_run=dry)
        success = dry or not urls or status in (200, 202)
    else:
        success = notify(dry_run=dry)
    sys.exit(0 if success else 1)
