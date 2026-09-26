"""Exchange sessions and the free, best-effort Yahoo chart adapter.

Quote timestamps are observations, not fetch times. Never synthesize a missing bar.
"""
from datetime import datetime, timedelta, timezone
from functools import lru_cache
import json
import math
import urllib.request
from zoneinfo import ZoneInfo

import exchange_calendars as xcals

from .core import ASSETS

UTC = timezone.utc
NY = ZoneInfo("America/New_York")


def utcnow():
    return datetime.now(UTC)


def timestamp(value):
    dt = datetime.fromisoformat(value) if isinstance(value, str) else value
    if dt.tzinfo is None:
        raise ValueError("Timestamp must include its timezone.")
    return dt.astimezone(UTC)


@lru_cache(maxsize=1)
def calendar():
    return xcals.get_calendar("XNYS", start="2000-01-01", end="2040-12-31")


def sessions(start, end):
    return [s.date().isoformat() for s in calendar().sessions_in_range(start, end)]


def close_time(day):
    return calendar().session_close(day).to_pydatetime()


def target_session(day, horizon):
    return calendar().session_offset(day, horizon).date().isoformat()


def market_state(now):
    now = timestamp(now)
    day = now.astimezone(NY).date().isoformat()
    cal = calendar()
    is_session = cal.is_session(day)
    opened = is_session and cal.session_open(day).to_pydatetime() <= now < close_time(day)
    latest = cal.date_to_session(day, direction="previous").date().isoformat()
    if now < close_time(latest):
        latest = target_session(latest, -1)
    return {"open": bool(opened), "session": day, "latest_completed": latest}


def positive(value, label="price"):
    if isinstance(value, bool):
        raise ValueError(f"Invalid {label}.")
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Missing or invalid {label}.") from None
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{label} must be finite and positive.")
    return value


def validate_quote(quote, now):
    if quote.get("symbol") not in ASSETS or quote.get("currency") != "USD":
        raise ValueError("Unsupported symbol or currency.")
    positive(quote.get("price"))
    observed = timestamp(quote["observed_at"])
    fetched = timestamp(quote["fetched_at"])
    if observed > timestamp(now) or observed > fetched or fetched > timestamp(now):
        raise ValueError("Quote observation cannot be in the future.")
    day = observed.astimezone(NY).date().isoformat()
    if not calendar().is_session(day):
        raise ValueError("Quote is not from a trading session.")
    if not calendar().session_open(day).to_pydatetime() <= observed <= close_time(day):
        raise ValueError("Expected a regular-session observation.")
    return quote


def quote_status(quote, now):
    if not quote:
        return "unavailable"
    observed = timestamp(quote["observed_at"])
    status = market_state(now)
    observed_day = observed.astimezone(NY).date().isoformat()
    if status["open"]:
        return "current" if observed_day == status["session"] and timestamp(now) - observed <= timedelta(minutes=30) else "stale"
    return "closed" if observed_day == status["latest_completed"] else "stale"


def validate_history(rows, now=None):
    previous = None
    for row in rows:
        day = row["date"]
        if previous and day <= previous:
            raise ValueError("Daily dates must be unique and increasing.")
        if not calendar().is_session(day):
            raise ValueError(f"Not an exchange session: {day}.")
        if now is not None and close_time(day) > timestamp(now):
            raise ValueError(f"Incomplete daily session: {day}.")
        for symbol in ASSETS:
            positive(row.get(symbol), symbol)
        previous = day
    return rows


def require_contiguous(rows):
    validate_history(rows)
    if rows and sessions(rows[0]["date"], rows[-1]["date"]) != [r["date"] for r in rows]:
        raise ValueError("Missing expected trading session in daily history.")


class YahooProvider:
    name = "Yahoo Finance (unofficial, personal educational use)"

    def fetch(self, symbol, interval, period="5d"):
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={period}&interval={interval}&includePrePost=false"
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=12) as response:
            raw = response.read(5_000_001)
        if len(raw) > 5_000_000:
            raise ValueError("Provider response too large.")
        payload = json.loads(raw)
        chart = payload.get("chart", {})
        if chart.get("error") or not chart.get("result"):
            raise ValueError("Provider returned no usable chart data.")
        result = chart["result"][0]
        if result["meta"].get("symbol") != symbol or result["meta"].get("currency") != "USD":
            raise ValueError("Provider symbol/currency mismatch.")
        times = result.get("timestamp", [])
        closes = result["indicators"]["quote"][0]["close"]
        if len(times) != len(closes) or times != sorted(set(times)):
            raise ValueError("Invalid or duplicate provider timestamps.")
        return list(zip(times, closes))

    def quote(self, symbol, now):
        pairs = self.fetch(symbol, "5m")
        valid = [(t, positive(p)) for t, p in pairs if p is not None]
        if not valid:
            raise ValueError(f"No intraday observations for {symbol}.")
        t, price = valid[-1]
        return validate_quote({"symbol": symbol, "price": price, "currency": "USD",
                               "observed_at": datetime.fromtimestamp(t, UTC).isoformat(),
                               "fetched_at": timestamp(now).isoformat(), "source": self.name}, now)

    def history(self, symbol, now):
        result = []
        latest = market_state(now)["latest_completed"]
        # Prior-session bars only; today's Yahoo daily bar can remain provisional.
        for t, price in self.fetch(symbol, "1d", "5y"):
            day = datetime.fromtimestamp(t, UTC).astimezone(NY).date().isoformat()
            if day > latest or day >= timestamp(now).astimezone(NY).date().isoformat():
                continue
            if price is None:
                continue  # A missing session is caught by contiguous-window validation.
            if not calendar().is_session(day):
                raise ValueError(f"Invalid provider session {day}.")
            result.append({"date": day, "price": positive(price)})
        if not result:
            raise ValueError(f"No completed history for {symbol}.")
        return result
