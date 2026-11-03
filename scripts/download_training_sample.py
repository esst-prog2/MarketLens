"""Fetch the offline replay snapshot (or, with --universe, the wider harness snapshot).

python scripts/download_training_sample.py [--universe]

The end is fixed, so a re-download reproduces the file. Nothing is written if the
provider changed any close already in the replay snapshot: history is extended,
never rewritten. prices.csv (the legacy 2024 sample) is never touched.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from marketlens.market_data import require_contiguous

START, END = 1640995200, 1793664000  # 2022-01-01 and 2026-11-03 00:00 UTC: sessions to 2026-11-02.
SNAPSHOTS = {"replay": (("SPY", "IEF", "GLD"), "training"),
             "universe": (("SPY", "IEF", "GLD", "QQQ", "IWM"), "universe")}


def fetch(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={START}&period2={END}&interval=1d"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as response:
        data = json.load(response)["chart"]["result"][0]
    if data["meta"]["currency"] != "USD" or data["meta"]["symbol"] != symbol:
        raise ValueError("Unexpected symbol or currency.")
    closes = {datetime.fromtimestamp(t, timezone.utc).date().isoformat(): float(p)
              for t, p in zip(data["timestamp"], data["indicators"]["quote"][0]["close"]) if p is not None}
    return closes, url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", action="store_true", help="also QQQ and IWM, for scripts/contenders.py --universe")
    symbols, stem = SNAPSHOTS["universe" if parser.parse_args().universe else "replay"]
    prices, urls = {}, {}
    for symbol in symbols:
        prices[symbol], urls[symbol] = fetch(symbol)
    days = sorted(set.intersection(*(set(p) for p in prices.values())))
    rows = [{"date": day, **{s: prices[s][day] for s in symbols}} for day in days]
    require_contiguous(rows, symbols)
    # Every close already in the replay snapshot must come back unchanged.
    with (ROOT/"data/training_prices.csv").open(newline="", encoding="utf-8") as handle:
        known = list(csv.DictReader(handle))
    fresh = {r["date"]: r for r in rows}
    changed = [k["date"] for k in known for s in ("SPY", "IEF", "GLD")
               if k["date"] not in fresh or repr(fresh[k["date"]][s]) != k[s]]
    if changed:
        raise SystemExit(f"Provider revised or dropped earlier closes ({len(changed)}), first {changed[:3]}; nothing written.")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=["date", *symbols], lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    raw = output.getvalue().encode()
    (ROOT/f"data/{stem}_prices.csv").write_bytes(raw)
    (ROOT/f"data/{stem}_sources.json").write_text(json.dumps({
        "provider": "Yahoo Finance", "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "start": days[0], "end": days[-1], "rows": len(rows), "urls": urls,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "convention": "USD daily close, not dividend-adjusted; frozen educational historical snapshot."
    }, indent=2)+"\n", encoding="utf-8")
    print(f"Saved {len(rows)} validated sessions of {', '.join(symbols)}, {days[0]} through {days[-1]}.")


if __name__ == "__main__":
    main()
