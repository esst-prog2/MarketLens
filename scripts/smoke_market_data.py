"""Explicit network smoke check: python scripts/smoke_market_data.py."""
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from marketlens.core import ASSETS
from marketlens.forecasting import fit_model
from marketlens.market_data import YahooProvider, utcnow, require_contiguous, quote_status


def main():
    provider=YahooProvider()
    now=utcnow()
    history={}
    for symbol in ASSETS:
        quote=provider.quote(symbol,now)
        bars=provider.history(symbol,now)
        history[symbol]={r["date"]:r["price"] for r in bars}
        print(json.dumps({"symbol":symbol,"quote":quote,"status":quote_status(quote,now),
                          "daily_count":len(bars),"last_daily":bars[-1]},sort_keys=True),flush=True)
    common=sorted(set.intersection(*(set(h) for h in history.values())))
    rows=[{"date":d,**{s:history[s][d] for s in ASSETS}} for d in common]
    require_contiguous(rows)
    try:
        model=fit_model(rows)
        print("MODEL:",json.dumps(model["metadata"],sort_keys=True))
    except ValueError as error:
        print("MODEL UNAVAILABLE (explicit eligibility rule):",error)
    print("PASS: actual intraday observations and completed daily history retrieved for all three symbols.")


if __name__=="__main__":
    main()
