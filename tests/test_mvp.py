"""Deterministic MVP checks. No network; real-source checks are separate."""
from copy import deepcopy
from datetime import datetime, timedelta
from http.server import ThreadingHTTPServer
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from urllib.request import urlopen, Request

import numpy as np

from app import make_handler
from marketlens.core import ASSETS, load_prices
from marketlens.forecasting import evaluate, features, fit_model, metrics, predict
from marketlens.market_data import (UTC, YahooProvider, close_time, market_state,
    quote_status, require_contiguous, target_session, validate_history, validate_quote)
from marketlens.mvp import MVPService
from marketlens.service import Service
from marketlens.storage import connect, migrate, SCHEMA

ROOT = Path(__file__).resolve().parents[1]
ROWS = load_prices(ROOT / "data/training_prices.csv")


class FakeProvider:
    name = "deterministic fixture"

    def __init__(self):
        self.calls = 0
        self.fail = False
        self.price = {s: 100.0 for s in ASSETS}
        self.observed = datetime(2023, 1, 4, 16, tzinfo=UTC)
        self.entered = threading.Event()
        self.release = None

    def quote(self, symbol, now):
        self.calls += 1
        self.entered.set()
        if self.release:
            self.release.wait(5)
        if self.fail:
            raise OSError("fixture provider unavailable")
        return {"symbol": symbol, "currency": "USD", "price": self.price[symbol],
                "observed_at": self.observed.isoformat(), "fetched_at": now.isoformat(), "source": self.name}

    def history(self, symbol, now):
        self.calls += 1
        if self.fail:
            raise OSError("fixture provider unavailable")
        latest = market_state(now)["latest_completed"]
        return [{"date": r["date"], "price": r[symbol]} for r in ROWS if r["date"] <= latest]


class CalendarProviderTests(unittest.TestCase):
    def test_holidays_dst_early_close(self):
        self.assertEqual(target_session("2024-05-24", 1), "2024-05-28")
        self.assertEqual(close_time("2024-03-08").hour, 21)
        self.assertEqual(close_time("2024-03-11").hour, 20)
        self.assertEqual(close_time("2024-11-29").hour, 18)
        self.assertFalse(market_state(datetime(2024,11,29,18,1,tzinfo=UTC))["open"])
        self.assertEqual(market_state(datetime(2024,7,4,16,tzinfo=UTC))["latest_completed"], "2024-07-03")

    def test_freshness_and_validation(self):
        p=FakeProvider(); now=p.observed
        q=p.quote("SPY",now)
        self.assertEqual(quote_status(q,now+timedelta(minutes=30)), "current")
        self.assertEqual(quote_status(q,now+timedelta(minutes=31)), "stale")
        q["fetched_at"]=(now+timedelta(minutes=31)).isoformat()
        self.assertEqual(quote_status(q,now+timedelta(minutes=31)), "stale")
        self.assertEqual(quote_status(q,now+timedelta(hours=6)), "closed")
        self.assertEqual(quote_status(q,now+timedelta(days=1)), "stale")
        for price in (0,-1,float("nan"),float("inf"),True,None):
            with self.subTest(price=price), self.assertRaises(ValueError):
                validate_quote({**q,"price":price}, now+timedelta(hours=1))
        with self.assertRaises(ValueError):
            validate_quote({**q,"currency":"EUR"},now+timedelta(hours=1))

    def test_missing_duplicate_provisional_history(self):
        require_contiguous(ROWS)
        with self.assertRaises(ValueError): require_contiguous(ROWS[:30]+ROWS[31:])
        with self.assertRaises(ValueError): validate_history(ROWS[:2]+ROWS[1:2])
        with self.assertRaises(ValueError): validate_history(ROWS[:2],close_time(ROWS[1]["date"])-timedelta(seconds=1))

    def test_yahoo_response_fixtures(self):
        now=datetime(2024,1,3,16,tzinfo=UTC)
        ts=int(now.timestamp())
        for symbol in ASSETS:
            payload={"chart":{"result":[{"meta":{"symbol":symbol,"currency":"USD"},"timestamp":[ts],"indicators":{"quote":[{"close":[101.5]}]}}],"error":None}}
            with patch("urllib.request.urlopen",return_value=io.BytesIO(json.dumps(payload).encode())) as fetch:
                q=YahooProvider().quote(symbol,now)
                self.assertEqual(q["price"],101.5)
                self.assertEqual(fetch.call_args.kwargs["timeout"],12)
            payload["chart"]["result"][0]["timestamp"]=[ts,ts]
            with patch("urllib.request.urlopen",return_value=io.BytesIO(json.dumps(payload).encode())), self.assertRaises(ValueError):
                YahooProvider().quote(symbol,now)
            with patch.object(YahooProvider,"fetch",return_value=[(int(close_time("2024-01-02").timestamp()),100),(ts,101)]):
                self.assertEqual(YahooProvider().history(symbol,now),[{"date":"2024-01-02","price":100.0}])


class ForecastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=ROWS[:252]
        cls.model=fit_model(cls.rows)

    def test_chronology_and_frozen_calibration(self):
        m=self.model["metadata"]
        self.assertGreaterEqual(m["fit_sessions"],120)
        self.assertEqual(m["cal_sessions"],40)
        self.assertLess(m["fit_label_end"],m["cal_start"])
        self.assertEqual(target_session(m["cal_end"],5),m["cutoff"])
        scaler=self.model["classifier"].estimator[0]
        self.assertEqual(scaler.n_samples_seen_,m["fit_sessions"]*3)
        self.assertEqual(self.model["regressor"][0].n_samples_seen_,m["fit_sessions"]*3)
        expected=np.mean([features(self.rows,i,s) for i in range(20,20+m["fit_sessions"]) for s in ASSETS],axis=0)
        np.testing.assert_allclose(scaler.mean_,expected)

    def test_absent_flat_calibration_preserves_classes_without_fake_examples(self):
        model=fit_model(ROWS[:270])
        self.assertIn("Flat",model["metadata"]["classes"])
        self.assertNotIn("Flat",model["metadata"]["cal_classes"])
        self.assertEqual(sum(model["metadata"]["cal_classes"].values()),120)
        probabilities=model["classifier"].predict_proba(np.array([features(ROWS[:270],269,s) for s in ASSETS]))
        self.assertTrue(np.isfinite(probabilities).all())
        np.testing.assert_allclose(probabilities.sum(axis=1),1)

    def test_determinism_future_isolation_and_valid_outputs(self):
        future=deepcopy(ROWS)
        for row in future[252:]:
            for s in ASSETS: row[s]*=50
        second=fit_model(future[:252])
        self.assertEqual(self.model["metadata"],second["metadata"])
        self.assertEqual(predict(self.model,self.rows),predict(second,future[:252]))
        predictions=predict(self.model,self.rows)
        self.assertEqual(len(predictions),6)
        for r in predictions:
            if r["horizon"]==5: self.assertTrue(0<=r["confidence"]<=1)
            else: self.assertGreater(r["estimate"],0)
        with self.assertRaises(ValueError): predict(self.model,self.rows[:-1])
        with self.assertRaises(ValueError): fit_model(self.rows[:180])
        with self.assertRaises(ValueError): fit_model([{**r,**{s:100 for s in ASSETS}} for r in self.rows])
        with patch.object(self.model["regressor"],"predict",return_value=np.array([-2.,0.,0.])), self.assertRaises(ValueError):
            predict(self.model,self.rows)

    def test_errors_flat_baselines_and_bin_endpoints(self):
        base={"price":100,"momentum":"Down","direction":"Up","confidence":1.,"horizon":5}
        flat=evaluate(base,100)
        self.assertFalse(flat["correct"])
        self.assertEqual(flat["actual"],"Flat")
        price=evaluate({**base,"horizon":1,"estimate":100},102)
        self.assertEqual(price["error"],2)
        self.assertAlmostEqual(price["ape"],2/102)
        m=metrics([flat,price,{**base,"actual_close":None}])
        self.assertEqual(m["brier"],1)
        self.assertEqual(m["bins"][-1]["count"],1)
        self.assertEqual(m["pending"],1)
        self.assertEqual(m["mae"],2)
        self.assertEqual(m["last_close_mae"],2)
        self.assertIsNone(metrics([])["brier"])
        for confidence, index in ((0,0),(.2,1),(.4,2),(.6,3),(.8,4),(1,4)):
            summary=metrics([evaluate({**base,"confidence":confidence},102)])
            self.assertEqual(summary["bins"][index]["count"],1)


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/"mvp.sqlite3"
        self.now=datetime(2023,1,4,16,tzinfo=UTC)
        self.provider=FakeProvider()
        self.service=MVPService(ROOT/"data/training_prices.csv",self.db,self.provider,lambda:self.now)
        self.addCleanup(self.service.stop)

    def test_migration_preserves_legacy_and_rollback(self):
        path=Path(self.tmp.name)/"legacy.sqlite3"
        legacy=Service(ROOT/"data/prices.csv",path)
        legacy.create_portfolio("Balanced",10000)
        legacy.advance()
        before=legacy.snapshot()
        new=MVPService(ROOT/"data/training_prices.csv",path,self.provider,lambda:self.now)
        self.assertEqual({k:v for k,v in new.legacy_snapshot().items() if k not in ("mode","can_invest")},before)
        self.assertTrue(path.with_name(path.name+".pre-mvp.bak").exists())
        self.assertIsNone(new.snapshot("replay")["portfolio"])
        broken=Path(self.tmp.name)/"broken.sqlite3"
        with connect(broken) as db: db.execute("CREATE TABLE original(value)")
        with self.assertRaises(sqlite3.OperationalError): migrate(broken,SCHEMA+["INVALID SQL"])
        with connect(broken) as db:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0],0)
            self.assertEqual([r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")],["original"])

    def test_live_refresh_immutable_portfolio_and_outage(self):
        s=self.service
        self.assertFalse(s.snapshot()["can_invest"])
        with self.assertRaises(ValueError): s.create_portfolio("Balanced",10000)
        self.assertTrue(s.refresh())
        first=s.snapshot()
        self.assertEqual(len(first["history"]),6)
        s.create_portfolio("Balanced",10000)
        units=[h["units"] for h in s.snapshot()["portfolio"]["holdings"]]
        self.provider.price["SPY"]=110
        self.now+=timedelta(minutes=5);self.provider.observed=self.now
        s.refresh()
        after=s.snapshot()
        self.assertEqual(first["history"],after["history"])
        self.assertEqual(after["portfolio"]["value"],10500)
        self.assertEqual([h["units"] for h in after["portfolio"]["holdings"]],units)
        calls=self.provider.calls
        for _ in range(3): s.request_refresh();s.refresh();s.snapshot()
        self.assertEqual(calls,self.provider.calls)
        self.provider.fail=True;self.now+=timedelta(minutes=31)
        s.refresh();bad=s.snapshot()
        self.assertIn("error",bad["provider"]["status"])
        self.assertFalse(bad["portfolio"]["fresh"])
        self.assertEqual(bad["portfolio"]["value"],10500)
        self.assertEqual(bad["signals"][0]["quote"]["observed_at"],after["signals"][0]["quote"]["observed_at"])
        self.assertGreater(s.next_attempt,self.now+timedelta(minutes=5))
        self.assertIsNone(s.snapshot("replay")["portfolio"])

    def test_invalid_ingestion_cannot_replace_cache_and_gaps_block_model(self):
        s=self.service;s.refresh()
        original=s.snapshot()["signals"][0]["quote"]
        with self.assertRaises(ValueError): s.ingest_quotes([{**original,"price":float("nan")}],self.now)
        self.assertEqual(s.snapshot()["signals"][0]["quote"],original)
        with self.assertRaises(ValueError):
            s.ingest_history({"SPY":[{"date":"2023-01-04","price":100}]},self.now)
        self.assertEqual(len(s.history("current")),252)
        with connect(self.db) as db:
            db.execute("DELETE FROM m_bars WHERE symbol='IEF' AND day='2022-12-30'")
        s.reset("current")
        self.assertIsNone(s.snapshot()["model"])
        self.assertIn("Missing expected",s.snapshot()["training"]["runs"][0]["error"])
        self.assertEqual(s.snapshot()["history"],[])

    def test_restart_catchup_failure_recovery_and_mode_reset(self):
        s=self.service;s.refresh();s.create_portfolio("Balanced",10000)
        initial=s.snapshot();s.create_portfolio("Growth",500,"replay")
        restarted=MVPService(ROOT/"data/training_prices.csv",self.db,self.provider,lambda:self.now)
        restarted.refresh()
        self.assertEqual(initial["history"],restarted.snapshot()["history"])
        self.assertEqual(len(restarted.snapshot()["training"]["runs"]),1)
        self.now=datetime(2023,1,5,16,tzinfo=UTC);self.provider.observed=self.now
        restarted.trainer=lambda rows: (_ for _ in ()).throw(RuntimeError("test fitting failure"))
        restarted.refresh()
        self.assertEqual(restarted.snapshot()["model"],initial["model"])
        self.assertEqual(restarted.snapshot()["training"]["runs"][0]["status"],"failed")
        self.assertEqual(len(restarted.snapshot()["history"]),12) # latest cutoff only, no missed days
        self.now+=timedelta(minutes=5);restarted.trainer=fit_model;restarted.refresh()
        self.assertNotEqual(restarted.snapshot()["model"],initial["model"])
        self.assertEqual(len(restarted.snapshot()["history"]),12) # no rewrite on retry
        before_current=restarted.snapshot()
        restarted.reset("replay")
        self.assertIsNone(restarted.snapshot("replay")["portfolio"])
        self.assertEqual(restarted.snapshot()["history"],before_current["history"])
        self.assertEqual(restarted.snapshot()["portfolio"]["holdings"],before_current["portfolio"]["holdings"])
        with connect(self.db) as db:
            db.execute("INSERT INTO m_runs(mode,cutoff,status,started) VALUES ('current','2023-01-10','running',?)",(self.now.isoformat(),))
        again=MVPService(ROOT/"data/training_prices.csv",self.db,self.provider,lambda:self.now)
        self.assertIn("Interrupted",again.snapshot()["training"]["runs"][0]["error"])

    def test_worker_concurrency_and_responsive_api(self):
        s=self.service;self.provider.release=threading.Event()
        server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(s))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        s.start();self.assertTrue(self.provider.entered.wait(3));s.start()
        worker=s.worker
        start=time.monotonic()
        for _ in range(3):
            with urlopen(f"http://127.0.0.1:{server.server_port}/api/state?mode=current",timeout=2) as r:
                self.assertEqual(json.load(r)["mode"],"current")
        self.assertLess(time.monotonic()-start,2)
        self.assertFalse(s.refresh())
        self.assertIs(worker,s.worker)
        self.assertEqual(self.provider.calls,1)
        self.provider.release.set()
        s.stop()

    def test_replay_full_cohort_no_network_and_immutable_records(self):
        s=self.service
        first=s.snapshot("replay")["history"]
        with patch("urllib.request.urlopen",side_effect=AssertionError("Replay must not use network")):
            s.create_portfolio("Balanced",10000,"replay")
            for _ in range(26): s.advance()
        final=s.snapshot("replay")
        self.assertEqual(self.provider.calls,0)
        self.assertTrue(any(r["correct"] is False for r in final["history"]))
        self.assertGreater(final["performance"]["price_evaluated"],0)
        complete=[c for c in final["training"]["comparisons"] if c["status"]=="complete"]
        self.assertTrue(complete)
        c=complete[-1]
        self.assertEqual(c["older_metrics"]["evaluated"],60)
        self.assertEqual(c["newer_metrics"]["price_evaluated"],60)
        for original in first:
            current=next(r for r in final["history"] if r["date"]==original["date"] and r["symbol"]==original["symbol"] and r["horizon"]==original["horizon"])
            for field in ("model","confidence","estimate","issued_at","price","input_hash"):
                self.assertEqual(current[field],original[field])
        with connect(self.db) as db:
            for key in ("older","newer"):
                cutoff=db.execute("SELECT cutoff FROM m_models WHERE id=?",(c[key],)).fetchone()[0]
                self.assertLess(cutoff,c["start"])
        self.assertEqual(s.snapshot()["history"],[])


if __name__=="__main__":
    unittest.main()
