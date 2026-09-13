#!/usr/bin/env python3
"""Build the public GolfRaw Pro value page from the product model.

The page is marketing-only.  It does not contain checkout, entitlement, or
security logic; those remain in the existing Pro client and API surfaces.

Usage::

    python3 scripts/build_pro_page.py          # update pro.html
    python3 scripts/build_pro_page.py --check  # report drift without writing
"""

import argparse
import html
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE_PATH = ROOT / "pro.html"
sys.path.insert(0, str(ROOT))

from scripts import tool_inventory as inventory
from scripts.schema_normalizer import _pro_schema

THEME_BLOCK = '''<!-- THEME:START -->
  <link rel="preload" href="/public/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/public/fonts/plus-jakarta-sans-var.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/public/theme-golf.css?v=10">
  <script>document.documentElement.classList.add('gr-js');setTimeout(function(){document.documentElement.classList.add('gr-reveal-all')},2500)</script>
  <script src="/public/theme-golf.js?v=10" defer></script>
<!-- THEME:END -->
'''


def _escape(value):
    return html.escape(str(value), quote=True)


def _model():
    model = inventory.PRODUCT_MODEL
    free = model["free"]
    pro = model["pro"]
    if free["tool_count"] != inventory.tool_counts()["free"]:
        raise ValueError("Free product count must match the public tool inventory")
    if not pro["features"] or not all(feature["verified_current"] for feature in pro["features"]):
        raise ValueError("Only verified current Pro features may be marketed")
    return free, pro


def render_metadata(free, pro):
    return f'''  <title>{_escape(pro["title"])}</title>
  <meta name="description" content="{_escape(pro["description"])}">
  <link rel="canonical" href="{_escape(inventory.SITE + pro["route"])}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta property="og:site_name" content="GolfRaw">
  <meta name="application-name" content="GolfRaw">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{_escape(pro["title"])}">
  <meta property="og:description" content="{_escape(pro["description"])}">
  <meta property="og:url" content="{_escape(inventory.SITE + pro["route"])}">
  <meta property="og:image" content="{_escape(inventory.HUB_OG_IMAGE)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{_escape(pro["title"])}">
  <meta name="twitter:description" content="{_escape(pro["description"])}">
  <meta name="twitter:image" content="{_escape(inventory.HUB_OG_IMAGE)}">'''


def render_schema(free, pro):
    document = _pro_schema()
    payload = json.dumps(document, indent=2, ensure_ascii=False).replace("</script>", "<\\/script>")
    return f'''  <script type="application/ld+json">
{payload}
  </script>'''


def render_features(pro):
    return "\n".join(
        f'''        <article class="pro-feature">
          <div class="pro-feature-label">GolfRaw Pro</div>
          <h3>{_escape(feature["label"])}</h3>
          <p>{_escape(feature["summary"])}</p>
          <a href="{_escape(feature["route"])}">Open the related tool &rarr;</a>
        </article>'''
        for feature in pro["features"]
    )


def render_page():
    free, pro = _model()
    metadata = render_metadata(free, pro)
    schema = render_schema(free, pro)
    features = render_features(pro)
    page_url = inventory.SITE + pro["route"]
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
{metadata}
  <meta name="author" content="GolfRaw Editorial">
{schema}
  <link rel="preload" href="/public/fonts/archivo-var.woff2" as="font" type="font/woff2" crossorigin>
  <style>
    @font-face{{font-family:'Archivo';font-style:normal;font-weight:100 900;font-display:swap;src:url('/public/fonts/archivo-var.woff2') format('woff2')}}
    @font-face{{font-family:'IBM Plex Mono';font-style:normal;font-weight:400 700;font-display:swap;src:url('/public/fonts/ibm-plex-mono-400.woff2') format('woff2')}}
    :root{{--ink:#101511;--paper:#F3F4F0;--white:#fff;--green:#1F7A45;--muted:#5B665E;--line:#DADDD4;--maxw:1180px}}
    *{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font-family:'Archivo',system-ui,sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased}}
    a{{color:inherit}} .wrap{{max-width:var(--maxw);margin:0 auto;padding:0 20px}}
    .site-header{{position:sticky;top:0;z-index:2;background:var(--paper);border-bottom:3px solid var(--ink)}}
    .nav{{display:flex;align-items:center;justify-content:space-between;height:68px;max-width:var(--maxw);margin:0 auto;padding:0 20px}}
    .logo{{font-weight:900;font-size:26px;letter-spacing:-.04em;text-transform:uppercase;text-decoration:none}} .logo .raw{{color:var(--green)}}
    .nav-links{{display:flex;gap:0}} .nav-links a{{font-weight:700;font-size:12.5px;text-transform:uppercase;letter-spacing:.05em;padding:8px 14px;text-decoration:none}}
    .nav-links a:hover,.nav-links a.active{{background:var(--ink);color:#fff}}
    .hero{{background:var(--ink);color:#fff;border-bottom:4px solid var(--green);padding:64px 0 54px}}
    .eyebrow,.pro-feature-label{{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--green);font-weight:700}}
    h1{{max-width:760px;margin:14px 0 18px;font-size:clamp(36px,6vw,72px);line-height:.96;letter-spacing:-.045em;text-transform:uppercase}}
    .hero p{{max-width:680px;margin:0;color:#C8D8CC;font-size:18px;line-height:1.6}}
    main{{padding:42px 0 72px}} .intro{{max-width:760px;margin:0 0 28px;font-size:18px}}
    .lane-grid,.feature-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}
    .lane,.pro-feature,.access-note{{background:var(--white);border:2px solid var(--ink);padding:26px}}
    .lane h2,.feature-heading,.access-note h2{{margin:8px 0 10px;font-size:28px;line-height:1.05;letter-spacing:-.025em}}
    .lane p,.pro-feature p,.access-note p{{margin:0 0 16px;color:#334039}}
    .button,.pro-feature a{{display:inline-block;font-weight:800;text-transform:uppercase;letter-spacing:.06em;text-decoration:none}}
    .button{{padding:13px 18px;background:var(--ink);color:#fff;border:2px solid var(--ink)}} .button:hover{{background:var(--green);border-color:var(--green)}}
    .section-label{{margin:44px 0 12px;font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--muted);font-weight:700}}
    .feature-heading{{margin:0 0 18px;font-size:38px}} .pro-feature h3{{margin:8px 0 9px;font-size:24px;line-height:1.1}}
    .pro-feature a{{color:var(--green)}} .access-note{{margin-top:18px;border-color:var(--green)}}
    .access-note h2{{font-size:24px}} .access-note p:last-child{{margin-bottom:0}}
    .cta-row{{display:flex;flex-wrap:wrap;gap:12px;margin-top:28px}} .site-footer{{border-top:3px solid var(--ink);padding:26px 0 40px;font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.08em}}
    .site-footer nav{{display:flex;flex-wrap:wrap;gap:18px;margin-top:14px}} .site-footer a{{text-decoration:none}}
    @media(max-width:760px){{.nav{{height:auto;min-height:68px;align-items:flex-start;flex-direction:column;padding-top:14px;padding-bottom:12px}}.nav-links{{width:100%;flex-wrap:wrap;margin-top:10px}}.nav-links a{{padding:7px 10px 7px 0}}.lane-grid,.feature-grid{{grid-template-columns:1fr}}.hero{{padding:46px 0 40px}}}}
  </style>
{THEME_BLOCK}</head>
<body>
  <header class="site-header">
    <div class="nav">
      <a href="/" class="logo" aria-label="GolfRaw home"><img src="/logo.png" alt="GolfRaw" width="184" height="40" decoding="async" fetchpriority="high"></a>
      <nav class="nav-links" aria-label="Main navigation">
        <a href="/news">Latest News</a><a href="/pga-tour">PGA Tour</a><a href="/liv-golf">LIV Golf</a>
        <a href="/tournaments">Tournaments</a><a href="/guides">Guides</a><a href="/tools">Tools</a><a href="{_escape(pro["route"])}" class="active">Pro</a>
      </nav>
    </div>
  </header>

  <section class="hero">
    <div class="wrap">
      <div class="eyebrow">GolfRaw Pro · public product guide</div>
      <h1>Keep the tools free. Add the handover.</h1>
      <p>{_escape(pro["description"])}</p>
    </div>
  </section>

  <main>
    <div class="wrap">
      <p class="intro">GolfRaw has two clear lanes: the free tools do the calculations in your browser; Pro adds ways to bring in prepared launch-monitor data and package the results for a coach, fitter or player.</p>

      <div class="lane-grid">
        <section class="lane" aria-labelledby="free-title">
          <div class="eyebrow">The foundation</div>
          <h2 id="free-title">{free["tool_count"]} tools stay Free forever</h2>
          <p>{_escape(free["description"])}</p>
          <a class="button" href="{_escape(free["route"])}">Use the free tools &rarr;</a>
        </section>
        <section class="lane" aria-labelledby="pro-title">
          <div class="eyebrow">The current public Pro surface</div>
          <h2 id="pro-title">What Pro adds</h2>
          <p>Pro adds the two verified output features below. The underlying free calculations do not move behind a gate.</p>
          <a class="button" href="/tools-coach-report">Open the Coach Report preview &rarr;</a>
        </section>
      </div>

      <div class="section-label">GolfRaw Pro · verified current features</div>
      <h2 class="feature-heading">What Pro adds</h2>
      <div class="feature-grid">
{features}
      </div>

      <section class="access-note" aria-labelledby="access-title">
        <h2 id="access-title">How access works</h2>
        <p>Availability follows the existing Pro configuration. When no active plan is configured, these surfaces open as a preview. If a plan is active, the tool handles the existing upgrade or pass-restore flow.</p>
        <p>This page is a public product explanation only. It does not change calculations, entitlement checks or security boundaries.</p>
      </section>

      <div class="cta-row">
        <a class="button" href="/tools">Start with all 12 free tools &rarr;</a>
        <a class="button" href="/tools-standing-order">Open Standing Order &rarr;</a>
      </div>
    </div>
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <span>© 2026 GolfRaw — ALL RATINGS FINAL</span>
      <nav aria-label="Footer navigation"><a href="/privacy">PRIVACY</a><a href="/terms">TERMS</a><a href="/contact">CONTACT</a><a href="/">← FRONT PAGE</a></nav>
    </div>
  </footer>
</body>
</html>
'''


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check for drift without writing")
    args = parser.parse_args(argv)
    expected = render_page()
    current = PAGE_PATH.read_text(encoding="utf-8") if PAGE_PATH.exists() else None
    if args.check:
        if current != expected:
            print("pro.html is out of sync with scripts/tool_inventory.py")
            return 1
        print("pro.html is in sync with scripts/tool_inventory.py")
        return 0
    if current != expected:
        PAGE_PATH.write_text(expected, encoding="utf-8")
        print("updated pro.html from scripts/tool_inventory.py")
    else:
        print("pro.html already matches scripts/tool_inventory.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
