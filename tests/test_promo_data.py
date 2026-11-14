"""The promo page's data file says exactly what the committed measurement says."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_promo():
    text = (ROOT/"docs/promo-data.js").read_text(encoding="utf-8").strip()
    prefix = "window.MARKETLENS = "
    assert text.startswith(prefix) and text.endswith(";")
    return json.loads(text[len(prefix):-1])


def load_measurement():
    line = next(l for l in (ROOT/"scripts/contenders_output.txt").read_text(encoding="utf-8").splitlines()
                if l.startswith("JSON:"))
    return json.loads(line[len("JSON:"):])


class PromoDataTests(unittest.TestCase):
    def test_scoreboard_and_edge_match_the_committed_measurement(self):
        promo, measured = load_promo(), load_measurement()
        self.assertEqual(promo["board"], measured["board"])
        self.assertEqual(promo["edge"], measured["edge"])

    def test_every_call_is_there_and_adds_up_to_the_accuracy(self):
        promo = load_promo()
        for row in promo["board"]:
            hits = promo["calls"]["hits"].get(row["name"])
            if row["calls"] == 0:
                self.assertIsNone(hits)
                continue
            self.assertEqual(len(hits), row["calls"])
            self.assertAlmostEqual(hits.count("1") / len(hits), row["accuracy"])

    def test_rolling_lines_cover_the_same_sessions(self):
        rolling = load_promo()["rolling"]
        lengths = {name: len(line) for name, line in rolling.items()}
        self.assertEqual(set(lengths), {"always-up", "momentum-20", "logistic (calibrated-linear-v2)"})
        self.assertEqual(len(set(lengths.values())), 1)
        self.assertEqual(lengths["always-up"], 957 - 19)  # 20-session window over 957 sessions.
        self.assertTrue(all(0 <= p[1] <= 1 for line in rolling.values() for p in line))


if __name__ == "__main__":
    unittest.main()
