"""Contenders share one interface and are scored on the same observations."""
from pathlib import Path
import tempfile
import unittest

from marketlens.contenders import (AlwaysUp, Contender, LastClose, Logistic, Momentum, call,
                                   leaderboard, replay)
from marketlens.core import ASSETS, load_prices
from marketlens.mvp import MVPService

ROOT = Path(__file__).resolve().parents[1]
ROWS = load_prices(ROOT / "data/training_prices.csv")


def hand_rows():
    """26 real sessions with made-up closes: SPY rises, IEF falls, GLD rises then falls."""
    return [{"date": r["date"], "SPY": 100.0+i, "IEF": 200.0-i, "GLD": 50.0+i if i <= 20 else 70.0-(i-20)}
            for i, r in enumerate(ROWS[:26])]


class Peek(Contender):
    """Records the latest session it was ever shown."""
    name = "peek"

    def __init__(self):
        self.seen = []

    def fit(self, rows):
        self.seen.append(rows[-1]["date"])

    def predict(self, rows):
        self.seen.append(rows[-1]["date"])
        return [call(rows, s, 5, direction="Up") for s in ASSETS]


class LateStarter(AlwaysUp):
    """Has no answer on the first reference session, as a model without history yet."""
    name = "late"

    def predict(self, rows):
        return [] if len(rows) == 21 else super().predict(rows)


class ContenderTests(unittest.TestCase):
    def test_baselines_counted_by_hand(self):
        # Only reference 20 has its fifth session (25) in the sample: SPY Up, IEF Down,
        # GLD Down (70 -> 65). Always-up gets SPY only; momentum (row 20 vs row 0) says
        # Up/Down/Up and gets SPY and IEF. Every next-session move is exactly $1.
        board = {b["name"]: b for b in leaderboard(replay([AlwaysUp(), Momentum(), LastClose()], hand_rows(), 20))}
        self.assertEqual((board["always-up"]["calls"], board["always-up"]["accuracy"]), (3, 1/3))
        self.assertEqual((board["momentum-20"]["calls"], board["momentum-20"]["accuracy"]), (3, 2/3))
        self.assertEqual((board["last-close"]["estimates"], board["last-close"]["mae"]), (15, 1.0))
        self.assertIsNone(board["always-up"]["brier"])
        self.assertIsNone(board["last-close"]["accuracy"])
        self.assertIsNone(board["momentum-20"]["mae"])

    def test_no_contender_sees_a_session_after_its_reference(self):
        peek = Peek()
        replay([peek], hand_rows(), 20)
        references = [r["date"] for r in hand_rows()[20:]]
        self.assertEqual(peek.seen, [d for d in references for _ in range(2)])

    def test_scored_only_on_shared_observations(self):
        calls = replay([AlwaysUp(), LateStarter()], ROWS[:40], 20)
        board = {b["name"]: b for b in leaderboard(calls)}
        self.assertEqual(len([r for r in calls["always-up"] if r["horizon"] == 5]), 15*3)
        self.assertEqual(board["always-up"]["calls"], 14*3)
        self.assertEqual(board["late"]["calls"], 14*3)
        self.assertEqual(board["always-up"]["accuracy"], board["late"]["accuracy"])

    def test_logistic_contender_is_the_model_the_app_issues(self):
        start = MVPService.replay_start
        with tempfile.TemporaryDirectory() as folder:
            service = MVPService(ROOT/"data/training_prices.csv", Path(folder)/"t.sqlite3")
            for _ in range(5):
                service.advance("replay")
            app = {(r["date"], r["symbol"], r["horizon"]): r for r in service.snapshot("replay")["history"]}
        calls = replay([Logistic()], ROWS[:start+6], start)["logistic (calibrated-linear-v2)"]
        # Next-session estimates mature for references 251-255, the five-session call for 251.
        self.assertEqual(len(calls), 5*3 + 3)
        for record in calls:
            mine = app[(record["date"], record["symbol"], record["horizon"])]
            for field in ("direction", "confidence", "correct", "estimate", "error"):
                self.assertEqual(record[field], mine[field])


if __name__ == "__main__":
    unittest.main()
