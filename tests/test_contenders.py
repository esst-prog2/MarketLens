"""Contenders share one interface and are scored on the same observations."""
from pathlib import Path
import tempfile
import unittest

from marketlens.contenders import (AlwaysUp, Contender, LastClose, Logistic, Momentum, call, edge,
                                   leaderboard, replay, rolling)
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


def scored(day, correct=None, error=None):
    """One evaluated SPY call on reference session `day` (an index used as a date)."""
    horizon = 5 if correct is not None else 1
    return {"date": f"d{day:03d}", "symbol": "SPY", "horizon": horizon, "actual_close": 1.0,
            "direction": "Up" if horizon == 5 else None, "confidence": None, "correct": correct,
            "estimate": 1.0 if horizon == 1 else None, "error": error, "ape": error}


def blocks_of_five(pattern):
    """Thirty sessions: in block k the rival is right on pattern[k] of its five sessions."""
    return [i % 5 >= hits for hits in pattern for i in range(5)]


class ContenderTests(unittest.TestCase):
    def test_edge_counted_by_hand(self):
        # The model is always right. Rival "a" is right 4,3,4,3,4,3 times per five-session
        # block, so the block differences are 0.2,0.4,... : mean 0.3, sample sd
        # sqrt(6*0.1^2/5) = 0.109545, range 0.3 +- 1.96*0.109545/sqrt(6) = 0.087654.
        # Rival "b" is never right, so "a" is the best baseline.
        rival = blocks_of_five([4, 3, 4, 3, 4, 3])
        calls = {"model": [scored(i, True) for i in range(30)],
                 "a": [scored(i, not wrong) for i, wrong in enumerate(rival)],
                 "b": [scored(i, False) for i in range(30)]}
        result = edge(calls, "model")[5]
        self.assertEqual((result["against"], result["sessions"], result["verdict"]), ("a", 30, "better"))
        self.assertAlmostEqual(result["value"], 0.3)
        self.assertAlmostEqual(result["high"]-result["value"], 0.087654, places=6)
        # Model right 3,5,3,5,3,5 times per block against "a"'s 4,3,...: block differences
        # -0.2,0.4,... : mean 0.1, range +- 1.96*0.328634/sqrt(6) = 0.262962.
        calls["model"] = [scored(i, not wrong) for i, wrong in enumerate(blocks_of_five([3, 5, 3, 5, 3, 5]))]
        result = edge(calls, "model")[5]
        self.assertAlmostEqual(result["value"], 0.1)
        self.assertAlmostEqual(result["high"]-result["value"], 0.262962, places=6)
        self.assertEqual(result["verdict"], "no measurable difference")
        short = edge({name: records[:29] for name, records in calls.items()}, "model")[5]
        self.assertEqual((short["sessions"], short["verdict"], short["low"]), (29, "not enough history yet", None))

    def test_price_edge_lower_error_is_better(self):
        # The model's error is $1 lower on every session except the last of each block,
        # where it is $1 higher: block differences are all -0.6, so the range is a point.
        calls = {"model": [scored(i, error=1.0 if i % 5 == 4 else 0.0) for i in range(30)],
                 "last-close": [scored(i, error=0.0 if i % 5 == 4 else 1.0) for i in range(30)]}
        result = edge(calls, "model")[1]
        self.assertAlmostEqual(result["value"], -0.6)
        self.assertAlmostEqual(result["low"], -0.6)
        self.assertEqual((result["against"], result["verdict"]), ("last-close", "better"))
        self.assertNotIn(5, edge(calls, "model"))

    def test_rolling_accuracy_counted_by_hand(self):
        # Right on sessions 0-9, wrong on 10-20. Window 0-19: 10/20; window 1-20: 9/20.
        calls = {"model": [scored(i, i < 10) for i in range(21)]}
        self.assertEqual(rolling(calls)["model"], [{"date": "d019", "accuracy": 0.5}, {"date": "d020", "accuracy": 0.45}])
        self.assertEqual(rolling({"model": calls["model"][:19]})["model"], [])

    def test_pending_calls_are_not_scored(self):
        pending = {**scored(0, True), "actual_close": None, "correct": None}
        self.assertEqual(leaderboard({"model": [pending]})[0]["calls"], 0)

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

    def test_screen_leaderboard_equals_the_script(self):
        start = MVPService.replay_start
        with tempfile.TemporaryDirectory() as folder:
            service = MVPService(ROOT/"data/training_prices.csv", Path(folder)/"t.sqlite3")
            for _ in range(8):
                service.advance("replay")
            screen = service.snapshot("replay")["contenders"]
        calls = replay([AlwaysUp(), Momentum(), LastClose(), Logistic()], ROWS[:start+9], start)
        self.assertEqual(screen["board"], leaderboard(calls))
        self.assertEqual(screen["edge"], edge(calls, Logistic.name))
        self.assertEqual([b["calls"] for b in screen["board"]], [4*3, 4*3, 0, 4*3])
        self.assertEqual(screen["edge"][5]["verdict"], "not enough history yet")


if __name__ == "__main__":
    unittest.main()
