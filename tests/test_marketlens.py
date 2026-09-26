import csv
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from app import make_handler
from marketlens.core import ASSETS, HORIZON, LOOKBACK, allocation, load_prices, portfolio_value, signals
from marketlens.service import Service

ROOT = Path(__file__).resolve().parents[1]


class MarketLensTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "state.sqlite3"
        self.service = Service(ROOT / "data/prices.csv", self.db)

    def test_real_sample_has_valid_complete_chronological_prices(self):
        prices = load_prices(ROOT / "data/prices.csv")
        self.assertEqual(len(prices), 252)
        self.assertEqual(prices[0]["date"], "2024-01-02")
        self.assertEqual(prices[-1]["date"], "2024-12-31")

    def test_invalid_data_is_rejected_before_forecasting(self):
        samples = [
            ("date,SPY,IEF\n", "GLD"),
            ("date,SPY,IEF,GLD\n2024-01-01,,10,10\n", "SPY"),
            ("date,SPY,IEF,GLD\n2024-01-01,10,nan,10\n", "IEF"),
            ("date,SPY,IEF,GLD\n2024-01-01,10,10,-1\n", "GLD"),
            ("date,SPY,IEF,GLD\n2024-01-01,10,10,10\n2024-01-01,11,10,10\n", "unique"),
            ("date,SPY,IEF,GLD\nwrong,10,10,10\n", "date"),
        ]
        for content, expected in samples:
            with self.subTest(expected=expected):
                path = Path(self.tmp.name) / "invalid.csv"
                path.write_text(content, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, expected):
                    Service(path, Path(self.tmp.name) / "invalid.sqlite3")

    def test_portfolio_arithmetic_and_persistence(self):
        self.service.create_portfolio("Balanced", 10000)
        first = self.service.snapshot()
        self.assertAlmostEqual(first["portfolio"]["value"], 10000)
        self.service.advance()
        later = self.service.snapshot()
        prices = self.service.prices
        expected = sum(10000 * weight * prices[LOOKBACK+1][s] / prices[LOOKBACK][s]
                       for s, weight in {"SPY": .5, "IEF": .35, "GLD": .15}.items())
        self.assertAlmostEqual(later["portfolio"]["value"], expected)
        self.assertAlmostEqual(later["portfolio"]["profit"], expected-10000)
        reopened = Service(ROOT / "data/prices.csv", self.db)
        self.assertEqual(reopened.snapshot(), later)

    def test_price_change_changes_value_exactly(self):
        holdings = allocation("Balanced", 10000, {s: 100 for s in ASSETS})
        prices = {"SPY": 110, "IEF": 100, "GLD": 100}
        self.assertAlmostEqual(portfolio_value(holdings, prices), 10500)

    def test_invalid_portfolio_does_not_mutate_state(self):
        for value in [0, -1, 99, 1_000_001, float("nan"), float("inf"), "10000", True, None]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.service.create_portfolio("Balanced", value)
        with self.assertRaises(ValueError):
            self.service.create_portfolio("Unknown", 10000)
        self.assertIsNone(self.service.snapshot()["portfolio"])

    def test_cannot_overwrite_an_existing_portfolio(self):
        self.service.create_portfolio("Growth", 1000)
        before = self.service.snapshot()
        with self.assertRaises(ValueError):
            self.service.create_portfolio("Balanced", 10000)
        self.assertEqual(before, self.service.snapshot())

    def test_forecasts_mature_only_after_five_days(self):
        original = self.service.snapshot()["history"]
        for _ in range(HORIZON - 1):
            self.service.advance()
        self.assertEqual(self.service.snapshot()["performance"]["evaluated"], 0)
        self.service.advance()
        current = self.service.snapshot()
        self.assertEqual(current["performance"]["evaluated"], 3)
        for item in current["history"][-3:]:
            expected_return = self.service.prices[LOOKBACK+HORIZON][item["symbol"]] / item["price"] - 1
            self.assertAlmostEqual(item["return"], expected_return)
            expected_direction = "Up" if expected_return > 0 else "Down" if expected_return < 0 else "Flat"
            self.assertEqual(item["correct"], item["direction"] == expected_direction)
        for previous, now in zip(original, current["history"][-3:]):
            for key in ("price", "direction", "strength", "model"):
                self.assertEqual(previous[key], now[key])

    def test_future_prices_cannot_change_current_signals(self):
        before = self.service.snapshot()
        for row in self.service.prices[LOOKBACK+1:]:
            for symbol in ASSETS:
                row[symbol] *= 100
        after = self.service.snapshot()
        self.assertEqual(before["signals"], after["signals"])
        self.assertEqual(before["history"], after["history"])

    def test_full_replay_records_wrong_predictions_and_stops_at_end(self):
        self.service.create_portfolio("Conservative", 5000)
        for _ in range(len(self.service.prices) - LOOKBACK - 1):
            self.service.advance()
        end = self.service.snapshot()
        self.assertEqual(end["remaining"], 0)
        self.assertTrue(any(item["correct"] is False for item in end["history"]))
        self.assertEqual(end["performance"]["pending"], HORIZON * 3)
        with self.assertRaises(ValueError):
            self.service.advance()
        self.service.reset()
        fresh = self.service.snapshot()
        self.assertEqual(fresh["day"], 0)
        self.assertIsNone(fresh["portfolio"])
        self.assertEqual(len(fresh["history"]), 3)

    def test_different_dataset_cannot_reuse_stored_forecasts(self):
        path = Path(self.tmp.name) / "changed.csv"
        rows = load_prices(ROOT / "data/prices.csv")
        rows[0]["SPY"] += 1
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["date", *ASSETS])
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaisesRegex(ValueError, "dataset changed"):
            Service(path, self.db)

    def test_api_and_static_files(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.service))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(base + "/") as response:
                self.assertIn(b'id="onboarding"', response.read())
            with opener.open(base + "/journey.js") as response:
                self.assertIn("javascript", response.headers["Content-Type"])
            req = urllib.request.Request(base + "/api/portfolio", data=b'{"profile":"Balanced","balance":10000}', headers={"Content-Type":"application/json"})
            with opener.open(req) as response:
                self.assertEqual(json.load(response)["portfolio"]["initial"], 10000)
            req = urllib.request.Request(base + "/api/advance", data=b'{}', headers={"Content-Type":"application/json", "Origin":"https://example.org"})
            with self.assertRaises(urllib.error.HTTPError) as error:
                opener.open(req)
            self.assertEqual(error.exception.code, 403)
            req = urllib.request.Request(base + "/api/reset", data=b'[]', headers={"Content-Type":"application/json"})
            with self.assertRaises(urllib.error.HTTPError) as error:
                opener.open(req)
            self.assertEqual(error.exception.code, 400)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
