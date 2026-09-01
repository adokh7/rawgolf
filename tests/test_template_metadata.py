#!/usr/bin/env python3
"""Regression checks for template exposure and article metadata contamination."""

import json
import html
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.golfraw.com"
STALE_HEADLINE = "Oakmont Is Eating the Field Alive — and the USGA Planned It That Way"
STALE_IMAGE_ALT = (
    "The first green at Oakmont Country Club during US Open 2026 setup, "
    "with championship rough visible"
)
STALE_SCHEMA_IMAGE = f"{SITE}/public/img/oakmont-2026-setup-og.jpg"
TEMPLATE_URL = f"{SITE}/article-template"
TEMPLATE_ROUTE = "/article-template"
STALE_TOP_TITLE = "Oakmont Is Eating the Field Alive | GOLFRAW"
STALE_DESCRIPTION_PREFIX = "Average score 74.8"
STALE_PUBLISHED = "2026-06-13T07:30:00+02:00"
STALE_MODIFIED = "2026-06-13T09:42:00+02:00"
STALE_TAGS = {"US Open", "Oakmont", "Course Setup"}

CONTAMINATED_PAGES = {
    "greg-norman-1996-masters.html",
    "jean-van-de-velde-1999-open.html",
    "news-2026-brooks-koepka-pga-tour-return-season-verdict.html",
    "news-2026-brooks-koepka-wyndham-putting-stat-injury.html",
    "news-2026-cameron-smith-bedminster-liv-winning-margin.html",
    "news-2026-charley-hull-four-putt-anna-huang-pif-london.html",
    "news-2026-espn-pga-tour-playoffs-coverage-fedex-st-jude.html",
    "news-2026-golf-ball-rollback-paused-colin-montgomerie.html",
    "news-2026-jackson-koivun-tpc-southwind-fedex-st-jude.html",
    "news-2026-jason-day-wyndham-streak-ended.html",
    "news-2026-lee-westwood-liv-golf-bedminster-expectations.html",
    "news-2026-lexi-thompson-pregnant-baby-daughter-lpga.html",
    "news-2026-matt-mcquillan-obituary-pga-tour.html",
    "news-2026-megha-ganne-lpga-debut-inkster-award.html",
    "news-2026-memphis-championship-series-fedexcup.html",
    "news-2026-mcilroy-memphis-fedex-st-jude.html",
    "news-2026-michigan-golf-tournaments-rocket-classic-liv-cancelled.html",
    "news-2026-pinnacle-bank-championship-frankie-harris-59.html",
    "news-2026-scheffler-tour-championship-fedexcup-format-east-lake.html",
    "news-2026-solheim-cup-dewi-weber-dutch-eligibility-let.html",
    "news-2026-what-beginners-actually-search.html",
    "what-beginners-actually-search.html",
    "news-2026-wyndham-championship-brennan-fedexcup-bubble-resolution.html",
    "what-is-topgolf.html",
}

EXPECTED_REPAIRED_DATES = {
    "greg-norman-1996-masters.html": "2026-06-16",
    "jean-van-de-velde-1999-open.html": "2026-06-16",
    "news-2026-cameron-smith-bedminster-liv-winning-margin.html": "2026-08-07",
    "news-2026-matt-mcquillan-obituary-pga-tour.html": "2026-08-07",
    "news-2026-mcilroy-memphis-fedex-st-jude.html": "2026-08-07",
    "news-2026-what-beginners-actually-search.html": "2026-08-05",
    "what-beginners-actually-search.html": "2026-08-05",
}

TEMPLATE_GENERATORS = {
    "create_resolution.py",
    "fix_template.py",
    "gen_espn.py",
    "gen_ganne.py",
    "gen_lexi.py",
    "generate_article.py",
    "generate_charley_article.py",
    "generate_lee_article.py",
    "generate_michigan_article.py",
    "generate_scheffler_article.py",
    "make_article.py",
    "scripts/gen_liv_article.py",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.canonicals = []
        self.json_ld = []
        self.h1 = []
        self.lead_alts = []
        self.tag_text = []
        self._capture = None
        self._buffer = []
        self._in_tag_row = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            key = (attrs.get("name") or attrs.get("property") or "").lower()
            if key:
                self.meta.setdefault(key, []).append(attrs.get("content", ""))
        elif tag == "link" and "canonical" in attrs.get("rel", "").split():
            self.canonicals.append(attrs.get("href", ""))
        elif tag == "script" and attrs.get("type") == "application/ld+json":
            self._capture = "json"
            self._buffer = []
        elif tag == "h1":
            self._capture = "h1"
            self._buffer = []
        elif tag == "img" and attrs.get("alt"):
            self.lead_alts.append(attrs["alt"])
        elif tag == "nav" and "tag-row" in attrs.get("class", "").split():
            self._in_tag_row = True
        elif tag == "a" and self._in_tag_row:
            self._capture = "tag"
            self._buffer = []

    def handle_data(self, data):
        if self._capture:
            self._buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._capture == "json":
            self.json_ld.append("".join(self._buffer))
            self._capture = None
            self._buffer = []
        elif tag == "h1" and self._capture == "h1":
            self.h1.append(" ".join("".join(self._buffer).split()))
            self._capture = None
            self._buffer = []
        elif tag == "a" and self._capture == "tag":
            self.tag_text.append(" ".join("".join(self._buffer).split()))
            self._capture = None
            self._buffer = []
        elif tag == "nav" and self._in_tag_row:
            self._in_tag_row = False


def parse_page(path):
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    documents = []
    for block in parser.json_ld:
        try:
            documents.append(json.loads(block))
        except json.JSONDecodeError:
            continue
    return parser, documents


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def article_schema(documents):
    return next(
        (
            node
            for document in documents
            for node in objects(document)
            if node.get("@type") in ("Article", "NewsArticle")
        ),
        None,
    )


def production_html():
    ignored_dirs = {
        ".agents",
        ".gemini",
        ".github",
        ".git",
        ".system_generated",
        ".vercel",
        "__pycache__",
        "node_modules",
        "out",
    }
    return sorted(
        path
        for path in ROOT.rglob("*.html")
        if path.name != "article-template.html"
        and not ignored_dirs.intersection(path.parts)
    )


class TemplateMetadataTests(unittest.TestCase):
    def test_article_template_is_excluded_from_vercel_output(self):
        ignored = {
            line.strip()
            for line in (ROOT / ".vercelignore").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        self.assertIn("article-template.html", ignored)
        self.assertIn(".vercel", ignored)

    def test_no_production_page_links_to_article_template(self):
        offenders = []
        for path in production_html():
            source = path.read_text(encoding="utf-8")
            if re.search(r'href=["\']/??article-template(?:\.html)?(?:["\'#?])', source):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual([], offenders)

    def test_no_production_page_contains_oakmont_template_markers(self):
        offenders = []
        for path in production_html():
            source = path.read_text(encoding="utf-8")
            if any(
                marker in source
                for marker in (
                    STALE_HEADLINE,
                    STALE_TOP_TITLE,
                    STALE_DESCRIPTION_PREFIX,
                    STALE_IMAGE_ALT,
                    STALE_SCHEMA_IMAGE,
                    STALE_PUBLISHED,
                    STALE_MODIFIED,
                    TEMPLATE_URL,
                    TEMPLATE_ROUTE,
                )
            ) or all(
                f'content="{tag}"' in source
                for tag in sorted(STALE_TAGS)
            ):
                offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual([], offenders)

    def test_beginners_page_preserves_non_task_schema_and_image_markup(self):
        source = (ROOT / "news-2026-what-beginners-actually-search.html").read_text(
            encoding="utf-8"
        )
        self.assertIn('"@type": "BreadcrumbList"', source)
        self.assertIn(
            'rel="preload" as="image" href="/public/what-beginners-actually-search-800.webp"',
            source,
        )
        self.assertIn('loading="eager"', source)
        self.assertIn('fetchpriority="high"', source)
        self.assertIn('srcset="/public/what-beginners-actually-search-400.webp 400w', source)
        self.assertIn('sizes="(max-width: 700px) 100vw, 740px"', source)
        self.assertIn('decoding="async"', source)

    def test_fresh_generator_replaces_all_scaffold_metadata(self):
        with tempfile.TemporaryDirectory(prefix="template-metadata-test-") as raw_dir:
            temp = Path(raw_dir)
            (temp / "scripts").mkdir()
            shutil.copy2(ROOT / "article-template.html", temp / "article-template.html")
            shutil.copy2(ROOT / "articles.json", temp / "articles.json")
            shutil.copy2(ROOT / "scripts" / "fix_template_metadata.py", temp / "scripts" / "fix_template_metadata.py")
            shutil.copy2(ROOT / "scripts" / "image_markup.py", temp / "scripts" / "image_markup.py")
            shutil.copy2(ROOT / "scripts" / "article_schema.py", temp / "scripts" / "article_schema.py")

            generator = (ROOT / "generate_article.py").read_text(encoding="utf-8")
            generator = generator.replace(str(ROOT), str(temp))
            (temp / "generate_article.py").write_text(generator, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "generate_article.py"],
                cwd=temp,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

            output = temp / "news-2026-brooks-koepka-wyndham-putting-stat-injury.html"
            self.assertTrue(output.is_file())
            parser, documents = parse_page(output)
            article = article_schema(documents)
            canonical = parser.canonicals[0]
            title = re.search(r"<title>(.*?)</title>", output.read_text(encoding="utf-8")).group(1)
            title = html.unescape(title)
            self.assertNotIn("Oakmont", output.read_text(encoding="utf-8"))
            self.assertNotIn(TEMPLATE_URL, output.read_text(encoding="utf-8"))
            self.assertEqual(parser.meta["og:title"][0], title)
            self.assertEqual(parser.meta["og:description"][0], parser.meta["description"][0])
            self.assertEqual(parser.meta["og:url"][0], canonical)
            self.assertEqual(
                parser.meta["og:image"][0],
                f"{SITE}/public/brooks-koepka-wyndham-putting-pga-tour.webp",
            )
            self.assertNotEqual(parser.meta["og:image:alt"][0], STALE_IMAGE_ALT)
            self.assertEqual(article["headline"], parser.h1[0])
            self.assertEqual(article["mainEntityOfPage"], canonical)
            self.assertEqual(article["datePublished"], "2026-08-09")
            self.assertNotIn("dateModified", article)
            self.assertEqual(
                article["keywords"],
                ", ".join(parser.meta["article:tag"]),
            )

    def test_fresh_scaffold_replaces_visible_article_header(self):
        with tempfile.TemporaryDirectory(prefix="article-header-test-") as raw_dir:
            temp = Path(raw_dir)
            (temp / "scripts").mkdir()
            shutil.copy2(ROOT / "article-template.html", temp / "article-template.html")
            shutil.copy2(
                ROOT / "scripts" / "article_header.py",
                temp / "scripts" / "article_header.py",
            )
            shutil.copy2(
                ROOT / "scripts" / "image_markup.py",
                temp / "scripts" / "image_markup.py",
            )
            shutil.copy2(
                ROOT / "scripts" / "article_schema.py",
                temp / "scripts" / "article_schema.py",
            )
            generator = (ROOT / "create_hovland.py").read_text(encoding="utf-8")
            (temp / "create_hovland.py").write_text(generator, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "create_hovland.py"],
                cwd=temp,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

            source = (
                temp / "news-2026-hovland-one-shot-lead-tour-championship.html"
            ).read_text(encoding="utf-8")
            self.assertIn(
                "Hovland's One-Shot Lead Came From Six Straight Putts",
                source,
            )
            self.assertIn("Six putts from seven feet or longer built it.", source)
            self.assertNotIn("Oakmont Is Eating the Field Alive", source)
            self.assertNotIn("Average score: 74.8", source)
            self.assertNotIn(STALE_IMAGE_ALT, source)
            self.assertNotIn('property="article:tag" content="Oakmont"', source)
            self.assertNotIn(STALE_PUBLISHED, source)
            self.assertIn("<h2>The Six-Putt Survival Clinic</h2>", source)
            self.assertIn(
                "/public/hovland-one-shot-lead-tour-championship-2026.webp",
                source,
            )

    def test_representative_generators_are_clean_from_a_fresh_scaffold(self):
        cases = (
            (
                "generate_article.py",
                "news-2026-brooks-koepka-wyndham-putting-stat-injury.html",
                "2026-08-09",
            ),
            (
                "gen_espn.py",
                "news-2026-espn-pga-tour-playoffs-coverage-fedex-st-jude.html",
                "2026-08-12",
            ),
            (
                "make_article.py",
                "news-2026-what-beginners-actually-search.html",
                "2026-08-05",
            ),
            (
                "scripts/gen_liv_article.py",
                "news-2026-liv-golf-bedminster-crushers-six-over-par.html",
                "2026-08-10",
            ),
        )
        with tempfile.TemporaryDirectory(prefix="template-metadata-generators-") as raw_dir:
            temp = Path(raw_dir)
            (temp / "scripts").mkdir()
            shutil.copy2(ROOT / "article-template.html", temp / "article-template.html")
            shutil.copy2(ROOT / "articles.json", temp / "articles.json")
            shutil.copy2(
                ROOT / "scripts" / "fix_template_metadata.py",
                temp / "scripts" / "fix_template_metadata.py",
            )
            shutil.copy2(
                ROOT / "scripts" / "image_markup.py",
                temp / "scripts" / "image_markup.py",
            )
            shutil.copy2(
                ROOT / "scripts" / "article_schema.py",
                temp / "scripts" / "article_schema.py",
            )
            shutil.copy2(
                ROOT / "scripts" / "gen_liv_article.py",
                temp / "scripts" / "gen_liv_article.py",
            )

            for generator_name, output_name, expected_date in cases:
                generator = (ROOT / generator_name).read_text(encoding="utf-8")
                generator = generator.replace(str(ROOT), str(temp))
                generator_path = temp / generator_name
                generator_path.parent.mkdir(parents=True, exist_ok=True)
                generator_path.write_text(generator, encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, generator_name],
                    cwd=temp,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    0,
                    result.returncode,
                    f"{generator_name}: {result.stdout}{result.stderr}",
                )

                output = temp / output_name
                source = output.read_text(encoding="utf-8")
                parser, documents = parse_page(output)
                article = article_schema(documents)
                title_match = re.search(r"<title>(.*?)</title>", source)
                self.assertIsNotNone(title_match)
                title = html.unescape(title_match.group(1))
                self.assertNotIn(STALE_HEADLINE, source)
                self.assertNotIn(STALE_TOP_TITLE, source)
                self.assertNotIn(STALE_DESCRIPTION_PREFIX, source)
                self.assertNotIn(STALE_IMAGE_ALT, source)
                self.assertNotIn(STALE_SCHEMA_IMAGE, source)
                self.assertNotIn(STALE_PUBLISHED, source)
                self.assertNotIn(STALE_MODIFIED, source)
                self.assertNotIn(TEMPLATE_URL, source)
                self.assertEqual(parser.meta["og:title"][0], title)
                self.assertEqual(
                    parser.meta["og:description"][0],
                    parser.meta["description"][0],
                )
                self.assertEqual(parser.meta["og:url"][0], parser.canonicals[0])
                self.assertEqual(article["headline"], parser.h1[0])
                self.assertEqual(parser.meta["article:published_time"][0], expected_date)
                self.assertEqual(
                    parser.meta.get("article:modified_time", [None])[0],
                    article.get("dateModified"),
                )
                self.assertEqual(article["datePublished"], expected_date)
                self.assertEqual(article.get("dateModified"), parser.meta.get("article:modified_time", [None])[0])
                main_entity = article["mainEntityOfPage"]
                if isinstance(main_entity, dict):
                    main_entity = main_entity.get("@id")
                self.assertEqual(main_entity, parser.canonicals[0])

    def test_template_generators_finalize_metadata_before_writing(self):
        missing = [
            filename
            for filename in sorted(TEMPLATE_GENERATORS)
            if "finalize_html" not in (ROOT / filename).read_text(encoding="utf-8")
        ]
        self.assertEqual([], missing)

    def test_each_contaminated_page_has_page_specific_article_metadata(self):
        registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
        records = {f"{a['slug']}.html": a for a in registry["articles"]}
        failures = []
        for filename in sorted(CONTAMINATED_PAGES):
            path = ROOT / filename
            parser, documents = parse_page(path)
            article = article_schema(documents)
            record = records[filename]
            canonical = parser.canonicals[0]
            published_meta = parser.meta["article:published_time"][0]
            modified_meta = parser.meta["article:modified_time"][0]
            if not article:
                failures.append(f"{filename}: missing Article/NewsArticle JSON-LD")
                continue
            main_entity = article.get("mainEntityOfPage")
            if isinstance(main_entity, dict):
                main_entity = main_entity.get("@id")
            checks = {
                "headline": article.get("headline") in {
                    parser.h1[0],
                    html.unescape(record.get("title", "")),
                },
                "mainEntityOfPage": main_entity == canonical,
                "image": record["image"] in json.dumps(article.get("image", "")),
                "datePublished": article.get("datePublished") == published_meta,
                "dateModified": article.get("dateModified") == modified_meta,
                "og:image:alt": bool(parser.lead_alts) and parser.lead_alts[0] != STALE_IMAGE_ALT,
                "article tags": parser.meta.get("article:tag")
                and parser.meta["article:tag"] != ["US Open", "Oakmont", "Course Setup"],
            }
            expected_date = EXPECTED_REPAIRED_DATES.get(filename)
            if expected_date:
                checks["visible byline date"] = (
                    published_meta == expected_date
                    and modified_meta == expected_date
                    and article.get("datePublished") == expected_date
                    and article.get("dateModified") == expected_date
                )
            failures.extend(f"{filename}: {field}" for field, passed in checks.items() if not passed)
        self.assertEqual([], failures)


if __name__ == "__main__":
    unittest.main()
