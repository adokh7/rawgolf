#!/usr/bin/env python3
"""Push new content at search engines instead of waiting to be crawled.

  python3 scripts/fast_index.py                 # ping WebSub + submit changed URLs
  python3 scripts/fast_index.py --websub        # WebSub hub ping only
  python3 scripts/fast_index.py --indexnow URL… # submit specific URLs
  python3 scripts/fast_index.py --dry-run       # show what would be sent

Two independent channels, because no single one reaches everybody:

  WebSub (PubSubHubbub) — publisher pings a hub, the hub immediately fetches
  feed.xml and fans it out to every subscriber. Google's public hub at
  pubsubhubbub.appspot.com is a subscriber, which makes this the closest
  remaining replacement for the retired sitemap-ping endpoint.

  IndexNow — a direct submit API shared by Bing, Yandex, Seznam and Naver.
  Google has publicly said it does NOT use IndexNow, so this covers everyone
  except Google. Both channels together is the point.

Stdlib only: this runs in CI and on a bare machine with no pip install.
"""
import sys, os, json, ssl
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
    urls = [u if u.startswith('http') else SITE + ('' if u.startswith('/') else '/') + u
            for u in urls]
    urls = [u for u in dict.fromkeys(urls) if u.startswith(SITE)]
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


def clear_pending():
    p = os.path.join(ROOT, '.fast-index-pending.json')
    if os.path.exists(p):
        os.remove(p)


def notify(urls=None, dry_run=False, verbose=True):
    """Fire both channels. Never raises — indexing is best-effort."""
    urls = pending_urls() if urls is None else urls
    if verbose:
        print(f'fast-index: {len(urls)} changed URL(s)')
    ping_websub(dry_run=dry_run, verbose=verbose)
    submit_indexnow(urls, dry_run=dry_run, verbose=verbose)
    if not dry_run:
        clear_pending()


if __name__ == '__main__':
    args = sys.argv[1:]
    dry = '--dry-run' in args
    args = [a for a in args if a != '--dry-run']
    if args and args[0] == '--websub':
        ping_websub(dry_run=dry)
    elif args and args[0] == '--indexnow':
        submit_indexnow(args[1:] or pending_urls(), dry_run=dry)
    else:
        notify(dry_run=dry)
