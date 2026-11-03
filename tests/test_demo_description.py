"""README section 1 (the final demo) must match what the program shows on that path."""
from pathlib import Path
import tempfile
import unittest

from marketlens.mvp import MVPService

ROOT = Path(__file__).resolve().parents[1]


def money(value):
    return f"${value:,.2f}"  # As web/app.js money() shows it.


def percent(value):
    return f"{value*100:.1f}%"  # As web/app.js percent() shows it.


def section_one():
    text = (ROOT/"README.md").read_text(encoding="utf-8")
    return text.split("## 1. THE DEMO", 1)[1].split("## 2.", 1)[0]


class DemoDescriptionTests(unittest.TestCase):
    def test_demo_numbers_come_from_the_program(self):
        with tempfile.TemporaryDirectory() as folder:
            s = MVPService(ROOT/"data/training_prices.csv", Path(folder)/"demo.sqlite3")
            s.create_portfolio("Balanced", 10000, "replay")
            entry = s.snapshot("replay")
            for _ in range(26):
                s.advance("replay")
            final = s.snapshot("replay")
        board = {b["name"]: b for b in final["contenders"]["board"]}
        model, up, close = board["logistic (calibrated-linear-v2)"], board["always-up"], board["last-close"]
        wrong = sum(r["correct"] is False for r in final["history"] if r["horizon"] == 5)
        holdings = {h["symbol"]: money(h["value"]) for h in entry["portfolio"]["holdings"]}
        edge = final["contenders"]["edge"][5]
        expected = [
            entry["date"], f"{final['day']} presses",
            f"{holdings['SPY']} of SPY, {holdings['IEF']} of IEF and {holdings['GLD']} of GLD",
            money(final["portfolio"]["value"]), f"{wrong} of its {model['calls']} five-session calls are wrong",
            f"its {percent(model['accuracy'])} accuracy", percent(up["accuracy"]),
            f"{money(model['mae'])} next-close error", f"{money(close['mae'])} of simply repeating",
            f"Not enough history yet ({edge['sessions']} of {edge['minimum']} shared sessions)"]
        text = section_one()
        for item in expected:
            self.assertIn(item, text)
        self.assertEqual(percent(model["accuracy"]), percent(up["accuracy"]))  # "exactly what always guessing Up gets"

    def test_demo_names_real_screens_and_controls(self):
        page = (ROOT/"web/index.html").read_text(encoding="utf-8") + (ROOT/"web/mvp.js").read_text(encoding="utf-8")
        text = section_one()
        for label in ("Historical replay — offline", "Practice", "Market outlook", "Apply fixed allocation",
                      "Next trading day", "Model history", "Contenders side by side"):
            self.assertIn(label, text)
            self.assertIn(label, page)


if __name__ == "__main__":
    unittest.main()
