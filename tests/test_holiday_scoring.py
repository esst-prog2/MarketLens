"""HW5 link to reality: a forecast is scored against the right day's close.

A test would go red if the program counted a market holiday as a trading day,
so an old forecast would be scored against the wrong day's price.

The expected values were counted by hand, outside the program, and written in
PLANNING_LOG.md (2026-10-11) before this test existed: a five-session forecast
issued on 2023-01-12 is due on 2023-01-20 because the NYSE was closed on
2023-01-16 (Martin Luther King Jr. Day), and the closes on that day were read by
hand from data/training_prices.csv.
"""
from pathlib import Path
import tempfile
import unittest

from marketlens.mvp import MVPService

ROOT = Path(__file__).resolve().parents[1]

ISSUED = "2023-01-12"
DUE = "2023-01-20"
EXPECTED = {"SPY": (395.88, "Down"), "IEF": (99.17, "Down"), "GLD": (179.28, "Up")}


class NoNetwork:
    name = "offline holiday test"

    def __getattr__(self, name):
        raise RuntimeError("Replay must not touch the network.")


class HolidayScoringTests(unittest.TestCase):
    def test_forecast_across_mlk_day_is_scored_against_fifth_trading_session(self):
        with tempfile.TemporaryDirectory() as folder:
            service = MVPService(ROOT/"data/training_prices.csv", Path(folder)/"hw5.sqlite3", NoNetwork())
            while service.history("replay")[-1]["date"] < DUE:
                service.advance("replay")
            history = service.snapshot("replay")["history"]
        for symbol, (close, direction) in EXPECTED.items():
            with self.subTest(symbol=symbol):
                record = next(r for r in history if r["date"] == ISSUED and r["symbol"] == symbol and r["horizon"] == 5)
                self.assertEqual(record["due"], DUE)
                self.assertIsNotNone(record["actual_close"], "The forecast was not scored on its due day.")
                self.assertAlmostEqual(record["actual_close"], close, delta=0.01)
                self.assertEqual(record["actual"], direction)


if __name__ == "__main__":
    unittest.main()
