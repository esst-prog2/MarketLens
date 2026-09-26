"""Fetch the fixed 2022–2024 offline training/replay snapshot; never replaces prices.csv."""
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


def main():
    symbols = ("SPY", "IEF", "GLD")
    prices, urls = {}, {}
    for symbol in symbols:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1=1640995200&period2=1735689600&interval=1d"
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as response:
            data = json.load(response)["chart"]["result"][0]
        if data["meta"]["currency"] != "USD" or data["meta"]["symbol"] != symbol:
            raise ValueError("Unexpected symbol or currency.")
        prices[symbol] = {datetime.fromtimestamp(t, timezone.utc).date().isoformat(): float(p)
                          for t, p in zip(data["timestamp"], data["indicators"]["quote"][0]["close"]) if p is not None}
        urls[symbol] = url
    days = sorted(set.intersection(*(set(p) for p in prices.values())))
    rows = [{"date": day, **{s: prices[s][day] for s in symbols}} for day in days]
    require_contiguous(rows)
    if len(rows) < 500:
        raise ValueError("Insufficient shared history.")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=["date", *symbols], lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    raw = output.getvalue().encode()
    (ROOT / "data/training_prices.csv").write_bytes(raw)
    (ROOT / "data/training_sources.json").write_text(json.dumps({
        "provider": "Yahoo Finance", "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "start": days[0], "end": days[-1], "rows": len(rows), "urls": urls,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "convention": "USD daily close, not dividend-adjusted; frozen educational historical snapshot."
    }, indent=2)+"\n", encoding="utf-8")
    print(f"Saved {len(rows)} validated sessions, {days[0]} through {days[-1]}.")


if __name__ == "__main__":
    main()
