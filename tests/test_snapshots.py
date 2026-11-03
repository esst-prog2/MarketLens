"""The replay snapshot is extended, never rewritten; the wider universe agrees with it."""
import csv
import hashlib
from pathlib import Path
import tempfile
import unittest

from marketlens.contenders import AlwaysUp, LastClose, Logistic, Momentum, leaderboard, replay
from marketlens.core import load_prices
from marketlens.forecasting import fit_model
from marketlens.market_data import require_contiguous
from marketlens.mvp import MVPService

ROOT = Path(__file__).resolve().parents[1]
ROWS = load_prices(ROOT/"data/training_prices.csv")
UNIVERSE = ("SPY", "IEF", "GLD", "QQQ", "IWM")
OLD_SHA = "3b9d0eab58ba52dbf4f08ae2084a6db9b78d3add147de62eedd995d589b8be1f"  # 2022-2024, retrieved 2026-09-26.


def write(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "SPY", "IEF", "GLD"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class SnapshotTests(unittest.TestCase):
    def test_extension_keeps_the_old_snapshot_byte_for_byte(self):
        # Line endings normalised: git may check the file out with CRLF on Windows.
        lines = (ROOT/"data/training_prices.csv").read_bytes().replace(b"\r\n", b"\n").split(b"\n")
        self.assertEqual(hashlib.sha256(b"\n".join(lines[:754]) + b"\n").hexdigest(), OLD_SHA)
        self.assertEqual((ROWS[0]["date"], ROWS[752]["date"], ROWS[-1]["date"], len(ROWS)),
                         ("2022-01-03", "2024-12-31", "2026-11-02", 1213))
        require_contiguous(ROWS)

    def test_older_database_continues_on_the_extended_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            old, db = Path(folder)/"old.csv", Path(folder)/"t.sqlite3"
            write(old, ROWS[:753])
            s = MVPService(old, db)
            for _ in range(3):
                s.advance("replay")
            before = s.snapshot("replay")["history"]
            s = MVPService(ROOT/"data/training_prices.csv", db)  # Accepted: a pure extension.
            self.assertEqual(s.snapshot("replay")["history"], before)
            self.assertEqual(s.snapshot("replay")["remaining"], 1213-1-(MVPService.replay_start+3))  # Past 2024-12-31.
            changed = [dict(r) for r in ROWS]
            changed[100]["SPY"] += 0.01
            write(old, changed)
            with self.assertRaisesRegex(ValueError, "new --database"):
                MVPService(old, db)

    def test_default_model_version_is_unchanged(self):
        # Computed with the code before symbol lists became a parameter (main, 2026-11-03).
        self.assertEqual(fit_model(ROWS[:252])["metadata"]["version"], "calibrated-linear-v2-30189143c9e5")
        self.assertNotIn("symbols", fit_model(ROWS[:252])["metadata"])

    def test_universe_shares_the_replay_closes(self):
        universe = load_prices(ROOT/"data/universe_prices.csv", UNIVERSE)
        self.assertEqual([{k: r[k] for k in ("date", "SPY", "IEF", "GLD")} for r in universe], ROWS)
        require_contiguous(universe, UNIVERSE)

    def test_contenders_on_five_instruments(self):
        universe = load_prices(ROOT/"data/universe_prices.csv", UNIVERSE)
        start = MVPService.replay_start
        calls = replay([c(UNIVERSE) for c in (AlwaysUp, Momentum, LastClose, Logistic)], universe[:start+7], start, UNIVERSE)
        board = {b["name"]: b for b in leaderboard(calls)}
        self.assertEqual(board[Logistic.name]["calls"], 2*5)  # References 251 and 252, five instruments.
        self.assertEqual(board[Logistic.name]["estimates"], 6*5)
        self.assertEqual({r["symbol"] for r in calls[Logistic.name]}, set(UNIVERSE))


if __name__ == "__main__":
    unittest.main()
