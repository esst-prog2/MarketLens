"""Download the reproducible 2024 price-only demo dataset (network required)."""
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    prices = {}
    sources = {}
    for symbol in ("SPY", "IEF", "GLD"):
        url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
               "?period1=1704067200&period2=1735689600&interval=1d")
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)["chart"]["result"][0]
        closes = result["indicators"]["quote"][0]["close"]
        prices[symbol] = {
            datetime.fromtimestamp(t, timezone.utc).date().isoformat(): round(p, 6)
            for t, p in zip(result["timestamp"], closes) if p is not None
        }
        sources[symbol] = url
    days = sorted(set.intersection(*(set(p) for p in prices.values())))
    if len(days) < 200:
        raise ValueError("Expected at least 200 shared trading days; sample not replaced.")
    target = ROOT / "data"
    target.mkdir(exist_ok=True)
    with (target / "prices.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(["date", *prices])
        for day in days:
            writer.writerow([day, *(prices[s][day] for s in prices)])
    (target / "sources.json").write_text(json.dumps({
        "provider": "Yahoo Finance", "downloaded_at": datetime.now(timezone.utc).isoformat(),
        "start": days[0], "end": days[-1], "rows": len(days), "urls": sources,
        "price_type": "Daily close in USD, not dividend-adjusted. Historical replay only."
    }, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(days)} shared trading days: {days[0]} to {days[-1]}.")


if __name__ == "__main__":
    main()
