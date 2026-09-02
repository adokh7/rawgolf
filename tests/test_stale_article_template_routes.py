import html
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


ROUTES = (
    {
        "output": "news-2026-hovland-leads-tour-championship-final-day.html",
        "h1": "Hovland Leads the Tour Championship by One Into Sunday",
        "title": "Hovland Leads the Tour Championship by One Into Sunday | GOLFRAW",
        "description": "He closed with six putts from 7 feet or longer to lead by one. Scheffler's three back, McIlroy shot 63, and nobody agrees on Sunday's tee times.",
        "canonical": "https://www.golfraw.com/news-2026-hovland-leads-tour-championship-final-day",
        "image": "https://www.golfraw.com/public/hovland-leads-tour-championship-final-day-2026.webp",
        "body_marker": "Leaderboard & Chasers Comparison",
    },
    {
        "output": "news-2026-hovland-one-shot-lead-tour-championship.html",
        "h1": "Hovland's One-Shot Lead Came From Six Straight Putts",
        "title": "Hovland's One-Shot Lead Came From Six Straight Putts",
        "description": "Six putts from seven feet or longer built it. Scheffler, Scott, Åberg and Gotterup are three back, McIlroy shot 63, and last place is 3 under.",
        "canonical": "https://www.golfraw.com/news-2026-hovland-one-shot-lead-tour-championship",
        "image": "https://www.golfraw.com/public/hovland-one-shot-lead-tour-championship-2026.webp",
        "body_marker": "The Six-Putt Survival Clinic",
    },
    {
        "output": "news-2026-michael-block-lead-ally-challenge.html",
        "h1": "Michael Block's 2-Shot Lead at the Ally Challenge Explained",
        "title": "Michael Block's 2-Shot Lead at the Ally Challenge Explained",
        "description": "He eagled the first, made five birdies, dropped nothing, and leads by two. But the number he's actually chasing isn't first place. Here's what it is.",
        "canonical": "https://www.golfraw.com/news-2026-michael-block-lead-ally-challenge",
        "image": "https://www.golfraw.com/public/michael-block-lead-ally-challenge-2026.webp",
        "body_marker": "Ally Challenge Round 2 Leaderboard",
    },
    {
        "output": "news-2026-michael-block-leads-ally-challenge-final-round.html",
        "h1": "Michael Block Leads the Ally Challenge Into Sunday by Two",
        "title": "Michael Block Leads the Ally Challenge Into Sunday by Two | GOLFRAW",
        "description": "He's in on an invitation, his son is on the bag, and he opened Saturday with an eagle. What Block actually needs from Sunday, and it isn't the trophy.",
        "canonical": "https://www.golfraw.com/news-2026-michael-block-leads-ally-challenge-final-round",
        "image": "https://www.golfraw.com/public/michael-block-leads-ally-challenge-final-round-2026.webp",
        "body_marker": "Leaderboard Standings (Top 10)",
    },
    {
        "output": "news-2026-pga-tour-winners-2026.html",
        "h1": "PGA Tour Winners 2026: 28 Names, 35 Events, One Left",
        "title": "PGA Tour Winners 2026: 28 Names, 35 Events, One Left",
        "description": "Every winner from the Sony Open to the BMW, the three men who won three times, and why the best player in the world isn't one of them.",
        "canonical": "https://www.golfraw.com/news-2026-pga-tour-winners-2026",
        "image": "https://www.golfraw.com/public/pga-tour-winners-2026-season-recap.webp",
        "body_marker": "The Complete 2026 PGA Tour Winners & Purses",
    },
    {
        "output": "news-2026-tiger-woods-career-money-list-record.html",
        "h1": "Tiger Woods' Career Money List Record May Fall Today",
        "title": "Tiger Woods' Career Money List Record May Fall Today",
        "description": "Scheffler needs solo 13th, McIlroy needs solo 4th. One outlet already declared it done a week ago. Here's what's actually verified and what isn't.",
        "canonical": "https://www.golfraw.com/news-2026-tiger-woods-career-money-list-record",
        "image": "https://www.golfraw.com/public/tiger-woods-career-money-list-record.webp",
        "body_marker": "Career Money List Thresholds & Stats",
    },
    {
        "output": "news-2026-tour-championship-final-round-hovland-leads.html",
        "h1": "Tour Championship Final Round: Hovland Leads by One",
        "title": "Tour Championship Final Round: Hovland Leads by One",
        "description": "Hovland leads by one at 15 under, Scheffler's three back, McIlroy shot 63. Every number that matters before the final round of the season.",
        "canonical": "https://www.golfraw.com/news-2026-tour-championship-final-round-hovland-leads",
        "image": "https://www.golfraw.com/public/tour-championship-final-round-hovland-leads-2026.webp",
        "body_marker": "How Hovland Seized the Lead",
    },
    {
        "output": "news-2026-tour-championship-round-3-tee-times-leaderboard.html",
        "h1": "Tour Championship Round 3: Hovland's 65 and Every Score",
        "title": "Tour Championship Round 3: Hovland's 65 and Every Score",
        "description": "Nineteen players began Saturday within five shots and it ended with a one-shot lead. Full Round 3 draw, results, and the Sunday sheet nobody agrees on.",
        "canonical": "https://www.golfraw.com/news-2026-tour-championship-round-3-tee-times-leaderboard",
        "image": "https://www.golfraw.com/public/tour-championship-2026-round-3-tee-times-leaderboard.webp",
        "body_marker": "The Pre-Round Chaos",
    },
    {
        "output": "news-2026-tour-championship-sunday-tee-times-round-4.html",
        "h1": "2026 Tour Championship Sunday Tee Times: Everything Moved",
        "title": "2026 Tour Championship Sunday Tee Times: Everything Moved",
        "description": "The whole draw shifted about an hour earlier and the pairings were rebuilt. Full Round 4 tee sheet, TV windows, and the mismatch nobody has flagged.",
        "canonical": "https://www.golfraw.com/news-2026-tour-championship-sunday-tee-times-round-4",
        "image": "https://www.golfraw.com/public/2026-tour-championship-sunday-tee-times-round-4.webp",
        "body_marker": "Revised Sunday Tee Times (Round 4)",
    },
    {
        "output": "why-pros-are-ditching-hybrids.html",
        "h1": "Why Pros Are Ditching Hybrids, and Why You Shouldn't",
        "title": "Why Pros Are Ditching Hybrids, and Why You Shouldn't",
        "description": "Hybrid use in the PGA Tour top 100 fell from 32% to 13%. On the LPGA it's 70%. The 15 mph gap explains both, and one man won a major with one.",
        "canonical": "https://www.golfraw.com/why-pros-are-ditching-hybrids",
        "image": "https://www.golfraw.com/public/why-pros-are-ditching-hybrids-analysis.webp",
        "body_marker": "Tour vs Amateur Hybrid & Long-Iron Data Comparison",
    },
    {
        "output": "news-every-shot-tiger-woods-80th-win-2018.html",
        "h1": "Every Shot From Tiger Woods' 80th Win: What to Watch For",
        "title": "Every Shot From Tiger Woods' 80th Win: What to Watch For",
        "description": "He shot 71 on Sunday, made three bogeys, and won by two. What the full broadcast shows that the highlight reel cuts, and the trophy he didn't take home.",
        "canonical": "https://www.golfraw.com/news-every-shot-tiger-woods-80th-win-2018",
        "image": "https://www.golfraw.com/public/every-shot-tiger-woods-80th-win-2018.webp",
        "body_marker": "Historical Performance: Tiger's 2018 East Lake Scorecard",
    },
)


def _text(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def _schema_nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _schema_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _schema_nodes(child)


class StaleArticleTemplateRoutesTests(unittest.TestCase):
    def test_all_affected_routes_render_page_specific_outputs(self):
        for case in ROUTES:
            with self.subTest(route=case["canonical"]):
                source = (ROOT / case["output"]).read_text(encoding="utf-8")

                title = _text(re.search(r"<title>(.*?)</title>", source, re.DOTALL).group(1))
                h1 = _text(re.search(r"<h1(?:\s+[^>]*)?>(.*?)</h1>", source, re.DOTALL).group(1))
                standfirst = _text(
                    re.search(
                        r'<p\s+class=["\']standfirst["\'][^>]*>(.*?)</p>',
                        source,
                        re.DOTALL,
                    ).group(1)
                )
                canonical = re.search(
                    r'<link\s+rel="canonical"\s+href="([^"]+)"', source
                ).group(1)
                og_image = re.search(
                    r'<meta\s+property="og:image"\s+content="([^"]+)"', source
                ).group(1)
                hero_image = re.search(
                    r'<figure\s+class="lead-img".*?<img\b[^>]*\bsrc="([^"]+)"',
                    source,
                    re.DOTALL,
                ).group(1)
                body = re.search(
                    r'<div\s+class="article-body">(.*?)</article>', source, re.DOTALL
                ).group(1)
                scripts = re.findall(
                    r'<script\s+type="application/ld\+json">(.*?)</script>',
                    source,
                    re.DOTALL,
                )
                schema = [json.loads(script) for script in scripts]
                articles = [
                    node
                    for document in schema
                    for node in _schema_nodes(document)
                    if node.get("@type") in {"Article", "NewsArticle"}
                ]
                self.assertEqual(1, len(articles))
                article = articles[0]

                self.assertEqual(case["title"], title)
                self.assertEqual(case["h1"], h1)
                self.assertEqual(case["description"], standfirst)
                self.assertEqual(case["canonical"], canonical)
                self.assertEqual(case["image"], og_image)
                self.assertEqual(case["image"].replace("https://www.golfraw.com", ""), hero_image)
                self.assertIn(case["body_marker"], body)
                self.assertIn(case["canonical"], json.dumps(article))
                self.assertIn(case["image"], json.dumps(article))
                self.assertIn(case["h1"], article["headline"])

                self.assertNotIn("Oakmont Is Eating the Field Alive", source)
                self.assertNotIn("Average score: 74.8", source)
                self.assertNotIn("oakmont-2026-setup-og.jpg", source)
                self.assertNotIn(
                    "The first green at Oakmont Country Club during US Open 2026 setup",
                    source,
                )
                self.assertNotIn('property="article:tag" content="Oakmont"', source)
                self.assertNotIn("2026-06-13T07:30:00+02:00", source)


if __name__ == "__main__":
    unittest.main()
