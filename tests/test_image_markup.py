import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

from scripts.image_markup import (
    audit_image_markup,
    image_dimensions,
    normalize_image_markup,
    responsive_candidates,
)
from scripts.sync_site import guide_card, news_card


ROOT = Path(__file__).resolve().parents[1]


class ImageTagParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "img":
            self.images.append(dict(attrs))

    def handle_startendtag(self, tag, attrs):
        if tag.lower() == "img":
            self.images.append(dict(attrs))


class ImageMarkupTests(unittest.TestCase):
    def test_reads_intrinsic_dimensions_from_source_asset(self):
        self.assertEqual(
            (1536, 1024),
            image_dimensions("/public/end-of-season-driver-deals-2026.webp", ROOT),
        )

    def test_discovers_only_existing_variants_with_real_width_descriptors(self):
        candidates = responsive_candidates(
            "/public/7-wood-vs-3-iron-australian-golfers.webp", ROOT
        )
        self.assertEqual(
            [
                (
                    "/public/7-wood-vs-3-iron-australian-golfers-400.webp",
                    400,
                ),
                (
                    "/public/7-wood-vs-3-iron-australian-golfers-800.webp",
                    800,
                ),
                (
                    "/public/7-wood-vs-3-iron-australian-golfers-1200.webp",
                    1200,
                ),
            ],
            candidates,
        )

    def test_card_generators_emit_real_dimensions(self):
        article = {
            "title": "Driver deals",
            "url": "/driver-deals",
            "image": "/public/end-of-season-driver-deals-2026.webp",
            "category": "GUIDES",
            "snippet": "A guide",
            "date": "2026-08-01",
        }
        news = news_card(article)
        guide = guide_card(article)
        for markup in (news, guide):
            self.assertIn('width="1536" height="1024"', markup)
            self.assertIn('400.webp 400w', markup)
            self.assertIn('800.webp 800w', markup)
            self.assertIn('1200.webp 1200w', markup)

    def test_normalizes_card_dimensions_responsive_markup_and_lazy_loading(self):
        source = (
            '<div class="news-grid"><article class="news">'
            '<img src="/public/7-wood-vs-3-iron-australian-golfers.webp" '
            'alt="Driver deals" loading="eager"></article></div>'
        )
        normalized = normalize_image_markup(source, ROOT / "news.html", ROOT)
        parser = ImageTagParser()
        parser.feed(normalized)
        image = parser.images[0]
        self.assertEqual("1672", image["width"])
        self.assertEqual("941", image["height"])
        self.assertIn("400w", image["srcset"])
        self.assertIn("800w", image["srcset"])
        self.assertEqual("(max-width: 700px) 92vw, 360px", image["sizes"])
        self.assertEqual("lazy", image["loading"])

    def test_normalizes_lead_as_eager_high_priority_and_secondary_as_lazy(self):
        source = """
        <main><article>
          <figure class="lead-img">
            <img src="/public/7-wood-vs-3-iron-australian-golfers.webp" alt="Lead" loading="lazy">
          </figure>
          <div class="article-body">
            <img src="/public/scottie-scheffler-3m-open-hole-14-hazard.webp" alt="Body">
          </div>
        </article></main>
        """
        normalized = normalize_image_markup(source, ROOT / "article.html", ROOT)
        parser = ImageTagParser()
        parser.feed(normalized)
        lead, secondary = parser.images
        self.assertEqual("1672", lead["width"])
        self.assertEqual("941", lead["height"])
        self.assertEqual("eager", lead["loading"])
        self.assertEqual("high", lead["fetchpriority"])
        self.assertEqual("(max-width: 700px) 100vw, 740px", lead["sizes"])
        self.assertEqual("lazy", secondary["loading"])
        self.assertEqual("1536", secondary["width"])
        self.assertEqual("1024", secondary["height"])

    def test_skips_remote_and_svg_images(self):
        source = (
            '<img src="https://example.com/remote.webp" alt="Remote">'
            '<img src="/public/logo.svg" alt="Logo">'
        )
        self.assertEqual(source, normalize_image_markup(source, ROOT / "x.html", ROOT))

    def test_normalization_is_idempotent(self):
        source = (
            '<div class="news-grid"><article class="news">'
            '<img src="/public/7-wood-vs-3-iron-australian-golfers.webp" alt="Card">'
            '</article></div>'
        )
        once = normalize_image_markup(source, ROOT / "news.html", ROOT)
        self.assertEqual(once, normalize_image_markup(once, ROOT / "news.html", ROOT))

    def test_production_inventory_has_no_missing_dimensions_or_eligible_srcsets(self):
        report = audit_image_markup(ROOT)
        self.assertEqual(0, report["missing_dimensions"])
        self.assertEqual(0, report["missing_srcset"])
        self.assertEqual(0, report["invalid_srcset_candidates"])
        self.assertEqual(0, report["dimension_mismatches"])

    def test_homepage_has_stable_lazy_card_images(self):
        report = audit_image_markup(ROOT)
        self.assertEqual(21, report["homepage_images"])
        self.assertEqual(0, report["homepage_missing_dimensions"])
        self.assertEqual(0, report["homepage_missing_srcset"])
        homepage = (ROOT / "index.html").read_text(encoding="utf-8")
        parser = ImageTagParser()
        parser.feed(homepage)
        self.assertEqual(21, len(parser.images))
        self.assertEqual(21, sum(image.get("loading") == "lazy" for image in parser.images))
        self.assertNotIn('rel="preload" as="image"', homepage)
        self.assertEqual(0, homepage.count('fetchpriority="high"'))


if __name__ == "__main__":
    unittest.main()
