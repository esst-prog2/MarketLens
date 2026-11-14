"""Export the promo page's data from the same replay as scripts/contenders.py.

python scripts/export_promo_data.py   (about two minutes; writes docs/promo-data.js)

The page draws only what this file holds: the scoreboard, the edge, the 20-session
rolling accuracy and, per contender, whether each scored five-session call was right.
It is a .js file (window.MARKETLENS = {...}) so the page also works opened from disk.
"""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from marketlens.contenders import CONTENDERS, Logistic, edge, leaderboard, replay, rolling, shared
from marketlens.core import load_prices
from marketlens.mvp import MVPService


def main():
    rows=load_prices(ROOT/"data/training_prices.csv")
    start=MVPService.replay_start
    calls=replay([c() for c in CONTENDERS],rows,start)
    keyed,keys=shared(calls)
    order=sorted(keys[5])  # (date, symbol, 5): the 2,871 shared five-session calls.
    hits={name:"".join("1" if records[k]["correct"] else "0" for k in order)
          for name,records in keyed.items() if any(k in records for k in order)}
    data={"source":"scripts/export_promo_data.py (same replay as scripts/contenders.py)",
          "instruments":["SPY","IEF","GLD"],"first":rows[start]["date"],"last":rows[-1]["date"],
          "model":Logistic.name,"board":leaderboard(calls),"edge":edge(calls,Logistic.name),
          "rolling":{name:[[p["date"],round(p["accuracy"],4)] for p in line] for name,line in rolling(calls).items()},
          "calls":{"order":"date, then symbol (GLD, IEF, SPY)","first":order[0][0],"last":order[-1][0],
                   "dates":sorted({k[0] for k in order}),"hits":hits}}
    out=ROOT/"docs/promo-data.js"
    out.write_text("window.MARKETLENS = "+json.dumps(data,separators=(",",":"),sort_keys=True)+";\n",encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}: {len(order)} shared calls, {sum(len(v) for v in data['rolling'].values())} rolling points")


if __name__=="__main__":
    main()
