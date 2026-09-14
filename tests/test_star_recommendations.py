import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "studio"))

import star_scanner
from project_recommendations import recommend


CATALOG = {
    "repositories": [
        {
            "repo": "QuantConnect/Lean",
            "score": 9.9,
            "tier": "core",
            "domain": "trading",
            "category": "Trading / quant / backtesting",
            "capabilities": ["backtesting", "execution", "portfolio", "xauusd"],
            "platforms": ["linux"],
            "languages": ["python", "c#"],
            "selfHosted": True,
            "bestFor": ["multi-asset backtesting", "live trading"],
            "avoidWhen": ["ultra-light exploratory notebooks"],
        },
        {
            "repo": "firecrawl/firecrawl",
            "score": 9.8,
            "tier": "core",
            "domain": "ai_agents",
            "category": "AI / web retrieval",
            "capabilities": ["web-retrieval"],
            "platforms": ["linux", "web"],
            "languages": ["typescript", "javascript"],
            "selfHosted": True,
            "bestFor": ["web extraction"],
        },
    ]
}


class StarScannerTests(unittest.TestCase):
    def test_structured_catalog_ranking_respects_constraints(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "catalog.json"
            path.write_text(json.dumps(CATALOG), encoding="utf-8")
            result = star_scanner.scan(
                ["xauusd", "backtesting", "execution"],
                str(path),
                domain="trading",
                capabilities=["backtesting"],
                platform="linux",
                language="python",
                self_hosted=True,
                top=5,
            )
            self.assertEqual(result["source_format"], "catalog-v1")
            self.assertEqual(result["repository_count"], 2)
            self.assertEqual([x["repo"] for x in result["matches"]], ["QuantConnect/Lean"])
            self.assertEqual(result["matches"][0]["tier"], "core")

    def test_markdown_parser_accepts_scored_rows(self):
        text = "- owner/repo — 9.7/10 — CORE\n- other/repo\n"
        self.assertEqual(star_scanner.parse_repositories(text), ["owner/repo", "other/repo"])

    def test_project_recommendation_writes_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            fake = {
                "source": "catalog",
                "source_format": "catalog-v1",
                "repository_count": 1,
                "needs": ["browser"],
                "matches": [{"repo": "firecrawl/firecrawl", "score": 90}],
            }
            with patch("project_recommendations.scan", return_value=fake) as mocked:
                result = recommend("browser", out, platform="web")
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["phase"], "browser")
            self.assertTrue((out / "star-recommendations.json").is_file())
            written = json.loads((out / "star-recommendations.json").read_text())
            self.assertEqual(written["matches"][0]["repo"], "firecrawl/firecrawl")
            self.assertEqual(mocked.call_args.kwargs["platform"], "web")


if __name__ == "__main__":
    unittest.main()
