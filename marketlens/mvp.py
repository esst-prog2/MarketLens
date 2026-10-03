"""Local current-data and deterministic replay application service."""
from datetime import timedelta
import json
from pathlib import Path
import pickle
import threading

from .core import ASSETS, PROFILES, allocation, load_prices, portfolio_value, signals
from .forecasting import data_hash, evaluate, fit_model, metrics, predict, track_record
from .market_data import (YahooProvider, calendar, close_time, market_state, quote_status,
                          require_contiguous, target_session, timestamp, utcnow, validate_history,
                          validate_quote)
from .storage import connect, migrate


def dump(value):
    return json.dumps(value, allow_nan=False, sort_keys=True)


class MVPService:
    is_mvp = True
    replay_start = 251

    def __init__(self, price_path, db_path, provider=None, clock=utcnow, trainer=fit_model):
        self.db_path = Path(db_path)
        self.clock, self.provider, self.trainer = clock, provider or YahooProvider(), trainer
        self.prices = load_prices(Path(price_path))
        require_contiguous(self.prices)
        if len(self.prices) <= self.replay_start + 26:
            raise ValueError("Replay history needs warm-up and at least 26 demonstration sessions.")
        self.locks = {mode: threading.RLock() for mode in ("current", "replay")}
        self.stop_event, self.wake_event = threading.Event(), threading.Event()
        self.worker = None
        self.next_attempt = None
        self.failures = 0
        self._models = {}
        migrate(self.db_path)
        with connect(self.db_path) as db:
            for mode in self.locks:
                db.execute("INSERT OR IGNORE INTO m_state(mode,cursor,dataset) VALUES (?,?,?)",
                           (mode, self.replay_start if mode == "replay" else None,
                            data_hash(self.prices) if mode == "replay" else None))
            if db.execute("SELECT dataset FROM m_state WHERE mode='replay'").fetchone()[0] != data_hash(self.prices):
                raise ValueError("Replay dataset changed. Start with a new --database path.")
            db.execute("UPDATE m_runs SET status='failed',error='Interrupted before completion',finished=? WHERE status='running'", (self.clock().isoformat(),))
        self.process("replay")

    @staticmethod
    def check_mode(mode):
        if mode not in ("current", "replay", "legacy"):
            raise ValueError("Choose current, replay or legacy mode.")

    def history(self, mode, db=None):
        if db is None:
            with connect(self.db_path) as connection:
                return self.history(mode, connection)
        if mode == "replay":
            cursor = db.execute("SELECT cursor FROM m_state WHERE mode=?", (mode,)).fetchone()[0]
            return self.prices[:cursor+1]
        grouped = {}
        for row in db.execute("SELECT * FROM m_bars ORDER BY day,symbol"):
            grouped.setdefault(row["day"], {"date": row["day"]})[row["symbol"]] = row["price"]
        return [row for row in grouped.values() if all(s in row for s in ASSETS)]

    def mode_now(self, mode, rows):
        return close_time(rows[-1]["date"]) + timedelta(seconds=1) if mode == "replay" else self.clock()

    def ingest_quotes(self, quotes, now):
        # Validate the entire supplied batch before any write; other instruments may be absent.
        for quote in quotes:
            validate_quote(quote, now)
        with connect(self.db_path) as db:
            for quote in quotes:
                old = db.execute("SELECT payload FROM m_quotes WHERE symbol=?", (quote["symbol"],)).fetchone()
                if old and timestamp(json.loads(old[0])["observed_at"]) > timestamp(quote["observed_at"]):
                    continue
                db.execute("INSERT OR REPLACE INTO m_quotes VALUES (?,?)", (quote["symbol"], dump(quote)))

    def ingest_history(self, by_symbol, now):
        # Validate complete instrument batches, preserving gaps instead of manufacturing bars.
        for symbol, items in by_symbol.items():
            if symbol not in ASSETS:
                raise ValueError("Unsupported history symbol.")
            check = [{"date": r["date"], **{s: r["price"] for s in ASSETS}} for r in items]
            validate_history(check, now)
        with connect(self.db_path) as db:
            for symbol, items in by_symbol.items():
                for row in items:
                    db.execute("INSERT OR REPLACE INTO m_bars VALUES (?,?,?,?,?)",
                               (symbol, row["date"], row["price"], self.provider.name, now.isoformat()))

    def _provider_status(self, payload):
        with connect(self.db_path) as db:
            db.execute("INSERT OR REPLACE INTO m_meta VALUES ('provider',?)", (dump(payload),))

    def refresh(self, force=False):
        now = self.clock()
        if self.next_attempt and now < self.next_attempt:
            return False
        if not self.locks["current"].acquire(blocking=False):
            return False
        try:
            errors = []
            self._provider_status({"status": "refreshing", "attempted_at": now.isoformat(), "errors": []})
            for symbol in ASSETS:
                try:
                    self.ingest_quotes([self.provider.quote(symbol, now)], now)
                except Exception as error:
                    errors.append(f"{symbol} quote: {error}")
            expected = market_state(now)["latest_completed"]
            with connect(self.db_path) as db:
                latest = {r["symbol"]: r["day"] for r in db.execute("SELECT symbol,max(day) AS day FROM m_bars GROUP BY symbol")}
            for symbol in ASSETS:
                if latest.get(symbol) != expected:
                    try:
                        self.ingest_history({symbol: self.provider.history(symbol, now)}, now)
                    except Exception as error:
                        errors.append(f"{symbol} history: {error}")
            self.process("current")
            self.failures = min(self.failures+1, 5) if errors else 0
            delay = min(3600, 300 * 2**self.failures)
            self.next_attempt = now + timedelta(seconds=delay)
            self._provider_status({"status": "cached / provider error" if errors else "ready",
                                   "attempted_at": now.isoformat(), "next_attempt": self.next_attempt.isoformat(),
                                   "errors": errors, "source": self.provider.name})
            self.record_value("current")
            return True
        finally:
            self.locks["current"].release()

    def start(self):
        if self.worker and self.worker.is_alive():
            return
        def work():
            while not self.stop_event.is_set():
                try:
                    self.refresh()
                except Exception as error:
                    self.next_attempt = self.clock()+timedelta(minutes=5)
                    self._provider_status({"status": "error", "errors": [str(error)], "next_attempt": self.next_attempt.isoformat()})
                self.wake_event.wait(1)
                self.wake_event.clear()
        self.worker = threading.Thread(target=work, name="marketlens-refresh", daemon=True)
        self.worker.start()

    def stop(self):
        self.stop_event.set()
        self.wake_event.set()
        if self.worker:
            self.worker.join(timeout=80)

    def request_refresh(self):
        self.wake_event.set()  # Honors cache/backoff even if several tabs request refresh.

    def _load_model(self, row):
        key = row["id"]
        if key not in self._models:
            # Only artifacts generated by this local application are read; no upload endpoint.
            self._models[key] = pickle.loads(row["artifact"])
        return self._models[key]

    def process(self, mode):
        with self.locks[mode]:
            rows = self.history(mode)
            if not rows:
                return
            now, cutoff = self.mode_now(mode, rows), rows[-1]["date"]
            with connect(self.db_path) as db:
                prices = {r["date"]: r for r in rows}
                for record in db.execute("SELECT id,symbol,due FROM m_forecasts WHERE mode=? AND actual IS NULL", (mode,)).fetchall():
                    if record["due"] in prices:
                        db.execute("UPDATE m_forecasts SET actual=? WHERE id=?", (prices[record["due"]][record["symbol"]], record["id"]))
                exists = db.execute("SELECT id FROM m_models WHERE mode=? AND cutoff=?", (mode, cutoff)).fetchone()
                run = db.execute("SELECT * FROM m_runs WHERE mode=? AND cutoff=? ORDER BY id DESC LIMIT 1", (mode, cutoff)).fetchone()
            retry_allowed = not run or not run["finished"] or now - timestamp(run["finished"]) >= timedelta(minutes=5)
            if not exists and retry_allowed:
                with connect(self.db_path) as db:
                    run_id = db.execute("INSERT INTO m_runs(mode,cutoff,status,started) VALUES (?,?,?,?)",
                                        (mode, cutoff, "running", now.isoformat())).lastrowid
                try:
                    model = self.trainer(rows)
                    metadata = model["metadata"]
                    identifier = mode + "-" + metadata["version"]
                    artifact = pickle.dumps(model, protocol=5)
                    with connect(self.db_path) as db:
                        previous = db.execute("SELECT * FROM m_models WHERE mode=? ORDER BY cutoff DESC LIMIT 1", (mode,)).fetchone()
                        db.execute("INSERT INTO m_models VALUES (?,?,?,?,?)", (identifier, mode, cutoff, dump(metadata), artifact))
                        if previous:
                            db.execute("INSERT INTO m_cohorts VALUES (?,?,?,?,?,?,?)",
                                       (previous["id"] + ":" + identifier, mode, previous["id"], identifier,
                                        target_session(cutoff, 1), target_session(cutoff, 20), target_session(cutoff, 25)))
                        db.execute("UPDATE m_runs SET status='succeeded',finished=? WHERE id=?", (now.isoformat(), run_id))
                    self._models[identifier] = model
                except Exception as error:
                    status = "not enough data" if isinstance(error, ValueError) else "failed"
                    with connect(self.db_path) as db:
                        db.execute("UPDATE m_runs SET status=?,finished=?,error=? WHERE id=?", (status, now.isoformat(), str(error), run_id))
            with connect(self.db_path) as db:
                current = db.execute("SELECT * FROM m_models WHERE mode=? AND cutoff<=? ORDER BY cutoff DESC LIMIT 1", (mode, cutoff)).fetchone()
                if current:
                    self._issue(db, mode, "main", current, rows, now)
                for cohort in db.execute("SELECT * FROM m_cohorts WHERE mode=? AND start<=? AND end>=?", (mode, cutoff, cutoff)).fetchall():
                    for key in ("older", "newer"):
                        version = db.execute("SELECT * FROM m_models WHERE id=?", (cohort[key],)).fetchone()
                        self._issue(db, mode, cohort["id"], version, rows, now)
            self.record_value(mode)

    def _issue(self, db, mode, series, model_row, rows, now):
        try:
            forecasts = predict(self._load_model(model_row), rows)
        except ValueError:
            return  # Incomplete feature windows cannot issue a new forecast.
        for record in forecasts:
            if mode == "current" and close_time(record["due"]) <= now:
                continue  # Never backfill live predictions for outcomes already observable.
            record.update({"model": model_row["id"], "issued_at": now.isoformat(), "mode": mode,
                           "input_hash": data_hash(rows), "actual_close": None, "correct": None,
                           "actual": None, "return": None, "error": None, "ape": None})
            db.execute("INSERT OR IGNORE INTO m_forecasts(mode,series,model,symbol,reference,horizon,due,payload) VALUES (?,?,?,?,?,?,?,?)",
                       (mode, series, record["model"], record["symbol"], record["date"], record["horizon"], record["due"], dump(record)))

    def quotes(self, mode, db, now):
        if mode == "replay":
            row = self.history(mode, db)[-1]
            return {s: {"symbol": s, "price": row[s], "observed_at": close_time(row["date"]).isoformat(),
                        "fetched_at": None, "source": "Yahoo Finance frozen historical snapshot", "status": "replay"} for s in ASSETS}
        result = {}
        for row in db.execute("SELECT * FROM m_quotes"):
            quote = json.loads(row["payload"])
            quote["status"] = quote_status(quote, now)
            result[row["symbol"]] = quote
        return result

    def create_portfolio(self, profile, balance, mode="current"):
        self.check_mode(mode)
        if mode == "legacy":
            raise ValueError("Legacy replay is read-only.")
        with self.locks[mode], connect(self.db_path) as db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT portfolio FROM m_state WHERE mode=?", (mode,)).fetchone()[0]
            if old:
                raise ValueError("A portfolio already exists. Reset this mode to start again.")
            quotes = self.quotes(mode, db, self.clock())
            if any(s not in quotes or quotes[s]["status"] not in ("current", "closed", "replay") for s in ASSETS):
                raise ValueError("All three entry quotes must be available and non-stale. Wait for fresh data or select replay.")
            prices = {s: quotes[s]["price"] for s in ASSETS}
            holdings = allocation(profile, balance, prices)
            started = self.history(mode, db)[-1]["date"] if mode == "replay" else self.clock().date().isoformat()
            p = {"profile": profile, "initial": balance, "holdings": holdings, "started": started,
                 "entries": quotes, "created_at": self.clock().isoformat()}
            db.execute("UPDATE m_state SET portfolio=? WHERE mode=?", (dump(p), mode))
        self.record_value(mode)

    def record_value(self, mode):
        with connect(self.db_path) as db:
            p = db.execute("SELECT portfolio FROM m_state WHERE mode=?", (mode,)).fetchone()[0]
            if not p:
                return
            quotes = self.quotes(mode, db, self.clock())
            if not all(s in quotes for s in ASSETS):
                return
            value = portfolio_value(json.loads(p)["holdings"], {s: quotes[s]["price"] for s in ASSETS})
            observed = max(q["observed_at"] for q in quotes.values())
            db.execute("INSERT OR REPLACE INTO m_values VALUES (?,?,?)", (mode, observed, value))

    def advance(self, mode="replay"):
        if mode != "replay":
            raise ValueError("Only historical replay can advance the simulated clock.")
        with self.locks[mode]:
            with connect(self.db_path) as db:
                cursor = db.execute("SELECT cursor FROM m_state WHERE mode=?", (mode,)).fetchone()[0]
                if cursor >= len(self.prices)-1:
                    raise ValueError("End of the historical sample.")
                db.execute("UPDATE m_state SET cursor=cursor+1 WHERE mode=?", (mode,))
            self.process(mode)

    def reset(self, mode="current"):
        self.check_mode(mode)
        if mode == "legacy":
            raise ValueError("Legacy replay is read-only.")
        with self.locks[mode], connect(self.db_path) as db:
            for table in ("m_forecasts", "m_runs", "m_models", "m_cohorts", "m_values"):
                db.execute(f"DELETE FROM {table} WHERE mode=?", (mode,))
            db.execute("UPDATE m_state SET portfolio=NULL,cursor=? WHERE mode=?", (self.replay_start if mode == "replay" else None, mode))
            self._models = {k: v for k, v in self._models.items() if not k.startswith(mode+"-")}
        self.process(mode)

    def _records(self, db, mode, series="main", model=None):
        records = []
        for row in db.execute("SELECT * FROM m_forecasts WHERE mode=? AND series=? ORDER BY reference DESC,symbol,horizon DESC", (mode, series)):
            if model and row["model"] != model:
                continue
            item = json.loads(row["payload"])
            records.append(evaluate(item, row["actual"]) if row["actual"] is not None else item)
        return records

    def snapshot(self, mode="current"):
        self.check_mode(mode)
        if mode == "legacy":
            return self.legacy_snapshot()
        now = self.clock()
        with connect(self.db_path) as db:
            db.execute("BEGIN")
            rows = self.history(mode, db)
            quotes = self.quotes(mode, db, now)
            saved = db.execute("SELECT * FROM m_state WHERE mode=?", (mode,)).fetchone()
            history = self._records(db, mode)
            model = db.execute("SELECT * FROM m_models WHERE mode=? ORDER BY cutoff DESC LIMIT 1", (mode,)).fetchone()
            runs = [dict(r) for r in db.execute("SELECT * FROM m_runs WHERE mode=? ORDER BY id DESC LIMIT 30", (mode,))]
            provider = db.execute("SELECT payload FROM m_meta WHERE key='provider'").fetchone()
            portfolio = None
            if saved["portfolio"]:
                p = json.loads(saved["portfolio"])
                items = [{"symbol": s, "name": ASSETS[s]["name"], "units": units,
                          "value": units*quotes[s]["price"] if s in quotes else None,
                          "observed_at": quotes.get(s, {}).get("observed_at"),
                          "status": quotes.get(s, {}).get("status", "unavailable"), "entry": p["entries"][s]}
                         for s, units in p["holdings"].items()]
                value = sum(h["value"] for h in items) if all(h["value"] is not None for h in items) else None
                for item in items:
                    item["weight"] = item["value"]/value if value is not None else None
                portfolio = {**p, "holdings": items, "value": value, "profit": value-p["initial"] if value is not None else None,
                             "return": value/p["initial"]-1 if value is not None else None,
                             "fresh": all(h["status"] in ("current", "closed", "replay") for h in items),
                             "chart": [{"date": r["observed"][:10], "value": r["value"]} for r in db.execute("SELECT * FROM m_values WHERE mode=? ORDER BY observed", (mode,))]}
            comparisons = []
            for cohort in db.execute("SELECT * FROM m_cohorts WHERE mode=? ORDER BY start DESC", (mode,)):
                old_records = self._records(db, mode, cohort["id"], cohort["older"])
                new_records = self._records(db, mode, cohort["id"], cohort["newer"])
                old_keys = {(r["date"], r["symbol"], r["horizon"]) for r in old_records}
                new_keys = {(r["date"], r["symbol"], r["horizon"]) for r in new_records}
                shared = old_keys & new_keys
                old_metrics = metrics([r for r in old_records if (r["date"], r["symbol"], r["horizon"]) in shared])
                new_metrics = metrics([r for r in new_records if (r["date"], r["symbol"], r["horizon"]) in shared])
                status = "complete" if new_metrics["evaluated"] == 60 and new_metrics["price_evaluated"] == 60 else "partial" if new_metrics["evaluated"] else "pending"
                comparisons.append({**dict(cohort), "status": status, "older_metrics": old_metrics, "newer_metrics": new_metrics})
            metadata = json.loads(model["metadata"]) if model else None
        display_signals = []
        recent = {s["symbol"]: s for s in signals(rows)} if len(rows) >= 21 else {}
        for symbol, asset in ASSETS.items():
            quote = quotes.get(symbol)
            forecast = next((r for r in history if r["symbol"] == symbol and r["horizon"] == 5), None)
            if forecast:
                forecast = {**forecast, "track_record": track_record(forecast, history)}
            price_forecast = next((r for r in history if r["symbol"] == symbol and r["horizon"] == 1), None)
            old = recent.get(symbol, {})
            display_signals.append({**asset, "symbol": symbol, "price": quote["price"] if quote else None,
                                    "quote": quote, "chart": old.get("chart", []), "risk": old.get("risk", "Unavailable"),
                                    "momentum": old.get("momentum", 0), "forecast": forecast,
                                    "price_forecast": price_forecast})
        return {"mode": mode, "date": rows[-1]["date"] if rows else None,
                "day": saved["cursor"]-self.replay_start if mode == "replay" else None,
                "remaining": len(self.prices)-saved["cursor"]-1 if mode == "replay" else 0,
                "profiles": PROFILES, "signals": display_signals, "portfolio": portfolio,
                "history": history, "performance": metrics(history), "model": model["id"] if model else None,
                "training": {"active": metadata, "runs": runs, "comparisons": comparisons},
                "versions": {v: metrics([r for r in history if r["model"] == v]) for v in sorted({r["model"] for r in history})},
                "provider": json.loads(provider[0]) if provider else {"status": "not fetched", "errors": []},
                "market": market_state(now), "can_invest": all(s in quotes and quotes[s]["status"] in ("current", "closed", "replay") for s in ASSETS)}

    def legacy_snapshot(self):
        with connect(self.db_path) as db:
            exists = db.execute("SELECT name FROM sqlite_master WHERE name='state'").fetchone()
            if not exists:
                raise ValueError("No legacy replay exists in this database.")
        from .service import Service
        legacy = object.__new__(Service)
        legacy.db_path = self.db_path
        legacy.prices = load_prices(Path(__file__).resolve().parents[1]/"data/prices.csv")
        result = legacy.snapshot()
        result.update({"mode": "legacy", "can_invest": False})
        return result
