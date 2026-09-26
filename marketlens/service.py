"""SQLite-backed replay state and immutable forecasts for one local user."""
import hashlib
from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3

from .core import ASSETS, HORIZON, LOOKBACK, MODEL, PROFILES, allocation, direction, load_prices, portfolio_value, signals


class Service:
    def __init__(self, price_path: Path, db_path: Path):
        self.prices = load_prices(price_path)
        self.db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        fingerprint = hashlib.sha256(price_path.read_bytes()).hexdigest()
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), day INTEGER NOT NULL,
                    profile TEXT, balance REAL, started INTEGER, holdings TEXT, dataset TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS forecasts (day INTEGER NOT NULL, symbol TEXT NOT NULL,
                    model TEXT NOT NULL, direction TEXT NOT NULL, strength INTEGER NOT NULL,
                    price REAL NOT NULL, PRIMARY KEY(day, symbol, model));
            """)
            db.execute("INSERT OR IGNORE INTO state(id, day, dataset) VALUES (1, ?, ?)", (LOOKBACK, fingerprint))
            if db.execute("SELECT dataset FROM state").fetchone()[0] != fingerprint:
                raise ValueError("Price dataset changed. Use a different --database path to start a new replay.")
            self.record(db)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def record(self, db):
        day = db.execute("SELECT day FROM state WHERE id=1").fetchone()[0]
        for signal in signals(self.prices[:day + 1]):
            db.execute("INSERT OR IGNORE INTO forecasts VALUES (?, ?, ?, ?, ?, ?)",
                       (day, signal["symbol"], MODEL, signal["direction"], signal["strength"], signal["price"]))

    def create_portfolio(self, profile, balance):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            state = db.execute("SELECT * FROM state WHERE id=1").fetchone()
            if state["holdings"] is not None:
                raise ValueError("A portfolio already exists. Reset the replay to start again.")
            holdings = allocation(profile, balance, self.prices[state["day"]])
            db.execute("UPDATE state SET profile=?, balance=?, started=day, holdings=? WHERE id=1",
                       (profile, balance, json.dumps(holdings)))

    def advance(self):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            day = db.execute("SELECT day FROM state WHERE id=1").fetchone()[0]
            if day >= len(self.prices) - 1:
                raise ValueError("You have reached the end of the historical sample.")
            db.execute("UPDATE state SET day=day+1 WHERE id=1")
            self.record(db)

    def reset(self):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("UPDATE state SET day=?, profile=NULL, balance=NULL, started=NULL, holdings=NULL WHERE id=1", (LOOKBACK,))
            db.execute("DELETE FROM forecasts")
            self.record(db)

    def snapshot(self):
        with self.connect() as db:
            db.execute("BEGIN")
            state = dict(db.execute("SELECT * FROM state WHERE id=1").fetchone())
            stored = db.execute("SELECT * FROM forecasts ORDER BY day DESC, symbol").fetchall()
        day = state["day"]
        current = self.prices[day]
        history = []
        for item in stored:
            item = dict(item)
            target = item["day"] + HORIZON
            matured = target <= day
            change = self.prices[target][item["symbol"]] / item["price"] - 1 if matured else None
            history.append({**item, "date": self.prices[item["day"]]["date"],
                            "due": self.prices[target]["date"] if target < len(self.prices) else None,
                            "return": change, "actual": direction(change) if matured else None,
                            "correct": direction(change) == item["direction"] if matured else None})
        evaluated = [item for item in history if item["correct"] is not None]
        portfolio = None
        if state["holdings"]:
            holdings = json.loads(state["holdings"])
            value = portfolio_value(holdings, current)
            portfolio = {"profile": state["profile"], "initial": state["balance"], "value": value,
                         "profit": value - state["balance"], "return": value / state["balance"] - 1,
                         "started": self.prices[state["started"]]["date"],
                         "holdings": [{"symbol": s, "name": ASSETS[s]["name"], "units": u,
                                       "value": u * current[s], "weight": u * current[s] / value}
                                      for s, u in holdings.items()],
                         "chart": [{"date": row["date"], "value": portfolio_value(holdings, row)}
                                   for row in self.prices[state["started"]:day + 1]]}
        return {"date": current["date"], "end": self.prices[-1]["date"], "day": day - LOOKBACK,
                "remaining": len(self.prices) - day - 1, "profiles": PROFILES,
                "signals": signals(self.prices[:day + 1]), "portfolio": portfolio,
                "history": history, "model": MODEL,
                "performance": {"evaluated": len(evaluated), "pending": len(history) - len(evaluated),
                                "accuracy": sum(x["correct"] for x in evaluated) / len(evaluated) if evaluated else None,
                                "always_up": sum(x["actual"] == "Up" for x in evaluated) / len(evaluated) if evaluated else None}}
