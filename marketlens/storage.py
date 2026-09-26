"""Additive transactional SQLite migration; legacy tables are never rewritten."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3

SCHEMA = [
    "CREATE TABLE IF NOT EXISTS m_state (mode TEXT PRIMARY KEY, cursor INTEGER, dataset TEXT, portfolio TEXT)",
    "CREATE TABLE IF NOT EXISTS m_quotes (symbol TEXT PRIMARY KEY, payload TEXT NOT NULL)",
    "CREATE TABLE IF NOT EXISTS m_bars (symbol TEXT, day TEXT, price REAL, source TEXT, fetched_at TEXT, PRIMARY KEY(symbol,day))",
    "CREATE TABLE IF NOT EXISTS m_models (id TEXT PRIMARY KEY, mode TEXT, cutoff TEXT, metadata TEXT, artifact BLOB, UNIQUE(mode,cutoff))",
    "CREATE TABLE IF NOT EXISTS m_runs (id INTEGER PRIMARY KEY, mode TEXT, cutoff TEXT, status TEXT, started TEXT, finished TEXT, error TEXT)",
    "CREATE TABLE IF NOT EXISTS m_forecasts (id INTEGER PRIMARY KEY, mode TEXT, series TEXT, model TEXT, symbol TEXT, reference TEXT, horizon INTEGER, due TEXT, payload TEXT, actual REAL, UNIQUE(mode,series,model,symbol,reference,horizon))",
    "CREATE UNIQUE INDEX IF NOT EXISTS main_forecast ON m_forecasts(mode,symbol,reference,horizon) WHERE series='main'",
    "CREATE TABLE IF NOT EXISTS m_cohorts (id TEXT PRIMARY KEY, mode TEXT, older TEXT, newer TEXT, start TEXT, end TEXT, due TEXT)",
    "CREATE TABLE IF NOT EXISTS m_values (mode TEXT, observed TEXT, value REAL, PRIMARY KEY(mode,observed))",
    "CREATE TABLE IF NOT EXISTS m_meta (key TEXT PRIMARY KEY, payload TEXT)",
]


@contextmanager
def connect(path):
    db = sqlite3.connect(path, timeout=15)
    db.row_factory = sqlite3.Row
    try:
        with db:
            yield db
    finally:
        db.close()


def migrate(path, statements=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    with connect(path) as db:
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version > 1:
            raise ValueError("Database was created by a newer MarketLens version.")
        if version == 1:
            return
        if existed:
            backup = path.with_name(path.name + ".pre-mvp.bak")
            if backup.exists():
                raise ValueError(f"Migration backup already exists: {backup}. Preserve it and use a new database path or restore intentionally.")
            with connect(backup) as dest:
                db.backup(dest)
        db.execute("BEGIN IMMEDIATE")
        for statement in SCHEMA if statements is None else statements:
            db.execute(statement)
        db.execute("PRAGMA user_version=1")
