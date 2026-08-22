#!/usr/bin/env python3
"""Regression checks for structured data on registered article pages."""

import json
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class JsonLdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._capturing = False
        self._buffer = []
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("type") == "application/ld+json":
            self._capturing = True
            self._buffer = []

    def handle_data(self, data):
        if self._capturing:
            self._buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._capturing:
            self.blocks.append("".join(self._buffer))
            self._capturing = False


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def article_documents():
    registry = json.loads((ROOT / "articles.json").read_text(encoding="utf-8"))
    for article in registry["articles"]:
        path = ROOT / f"{article['slug']}.html"
        if not path.exists():
            continue
        parser = JsonLdParser()
        parser.feed(path.read_text(encoding="utf-8"))
        documents = [json.loads(block) for block in parser.blocks]
        nodes = [node for document in documents for node in objects(document)]
        if any(node.get("@type") in ("Article", "NewsArticle") for node in nodes):
            yield path, nodes


class ArticleSchemaTests(unittest.TestCase):
    def test_general_articles_do_not_emit_event_schema(self):
        offenders = []
        for path, nodes in article_documents():
            events = [node.get("name", "unnamed event") for node in nodes
                      if node.get("@type") == "SportsEvent"]
            if events:
                offenders.append(f"{path.name}: {', '.join(events)}")
        self.assertEqual([], offenders)

    def test_dustin_johnson_page_has_complete_news_article(self):
        target = ROOT / "news-2026-dustin-johnson-liv-golf-2-0.html"
        parser = JsonLdParser()
        parser.feed(target.read_text(encoding="utf-8"))
        nodes = [node for block in parser.blocks for node in objects(json.loads(block))]
        article = next(node for node in nodes if node.get("@type") == "NewsArticle")
        required = {
            "headline", "description", "image", "datePublished", "dateModified",
            "author", "publisher", "mainEntityOfPage",
        }
        self.assertEqual(set(), required - article.keys())


if __name__ == "__main__":
    unittest.main()
