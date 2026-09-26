"""Validated price data, an explainable baseline, and portfolio arithmetic."""
import csv
from datetime import date
import math
from pathlib import Path
from statistics import stdev

ASSETS = {
    "SPY": {"name": "US equities", "description": "S&P 500 equity ETF"},
    "IEF": {"name": "US Treasury bonds", "description": "7–10 year Treasury ETF"},
    "GLD": {"name": "Gold", "description": "Gold-backed exchange-traded trust"},
}
PROFILES = {
    "Conservative": {"SPY": 0.20, "IEF": 0.65, "GLD": 0.15},
    "Balanced": {"SPY": 0.50, "IEF": 0.35, "GLD": 0.15},
    "Growth": {"SPY": 0.75, "IEF": 0.15, "GLD": 0.10},
}
LOOKBACK = 20
HORIZON = 5
MODEL = "momentum-20-v1"


def load_prices(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = {"date", *ASSETS} - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
        rows = []
        for number, raw in enumerate(reader, 2):
            try:
                day = date.fromisoformat(raw["date"]).isoformat()
            except (TypeError, ValueError):
                raise ValueError(f"Row {number}: invalid or missing date.") from None
            if rows and day <= rows[-1]["date"]:
                raise ValueError(f"Row {number}: dates must be unique and increasing.")
            row = {"date": day}
            for symbol in ASSETS:
                try:
                    price = float(raw[symbol])
                except (ValueError, TypeError):
                    raise ValueError(f"Row {number}: missing or invalid {symbol} price.") from None
                if not math.isfinite(price) or price <= 0:
                    raise ValueError(f"Row {number}: {symbol} must be a finite positive price.")
                row[symbol] = price
            rows.append(row)
    if len(rows) < LOOKBACK + HORIZON + 1:
        raise ValueError(f"At least {LOOKBACK + HORIZON + 1} complete price rows are required.")
    return rows


def direction(change):
    return "Up" if change > 0 else "Down" if change < 0 else "Flat"


def signals(history):
    """Only receives data available as of the simulated observation date."""
    if len(history) < LOOKBACK + 1:
        raise ValueError("Not enough price history to create a forecast.")
    result = []
    for symbol, asset in ASSETS.items():
        values = [row[symbol] for row in history[-LOOKBACK - 1:]]
        change = values[-1] / values[0] - 1
        returns = [b / a - 1 for a, b in zip(values, values[1:])]
        volatility = stdev(returns) * math.sqrt(252)
        # A descriptive strength score, deliberately not a probability.
        strength = round(min(100, abs(change) / max(volatility / math.sqrt(252) * math.sqrt(LOOKBACK), 0.001) * 50))
        result.append({
            "symbol": symbol, **asset, "price": values[-1], "direction": direction(change),
            "momentum": change, "strength": strength, "volatility": volatility,
            "risk": "Low" if volatility < 0.10 else "Moderate" if volatility < 0.20 else "High",
            "explanation": f"The price moved {change:+.1%} over 20 trading days. The baseline expects that direction to continue over the next 5 trading days.",
            "chart": values,
        })
    return result


def allocation(profile, balance, prices):
    if profile not in PROFILES:
        raise ValueError("Choose Conservative, Balanced or Growth.")
    if isinstance(balance, bool) or not isinstance(balance, (int, float)) or not math.isfinite(balance) or not 100 <= balance <= 1_000_000:
        raise ValueError("Starting balance must be a number from $100 to $1,000,000.")
    return {symbol: balance * weight / prices[symbol] for symbol, weight in PROFILES[profile].items()}


def portfolio_value(holdings, prices):
    return sum(units * prices[symbol] for symbol, units in holdings.items())
