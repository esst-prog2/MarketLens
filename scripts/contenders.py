"""All contenders side by side on the full snapshot replay.

python scripts/contenders.py             SPY, IEF, GLD (the app's instruments)
python scripts/contenders.py --universe  plus QQQ and IWM, from data/universe_prices.csv
"""
import argparse
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from marketlens.contenders import CONTENDERS, Logistic, edge, leaderboard, replay
from marketlens.core import load_prices
from marketlens.mvp import MVPService


def cell(value, form):
    return "—" if value is None else format(value, form)


UNIVERSE=("SPY","IEF","GLD","QQQ","IWM")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--universe",action="store_true",help="measure on SPY, IEF, GLD, QQQ and IWM")
    wide=parser.parse_args().universe
    symbols=UNIVERSE if wide else ("SPY","IEF","GLD")
    rows=load_prices(ROOT/("data/universe_prices.csv" if wide else "data/training_prices.csv"),symbols)
    start=MVPService.replay_start  # Same first practice session as Historical replay.
    started=time.perf_counter()
    calls=replay([c(symbols) for c in CONTENDERS],rows,start,symbols)
    seconds=time.perf_counter()-started
    board,edges=leaderboard(calls),edge(calls,Logistic.name)
    print(f"instruments {', '.join(symbols)}  sessions {rows[start]['date']}..{rows[-1]['date']}  references: {len(rows)-start}  seconds: {seconds:.1f}")
    print(f"{'contender':32} {'5-day calls':>11} {'accuracy':>9} {'brier':>7} {'1-day est.':>10} {'MAE $':>8} {'MAPE':>8}")
    for b in board:
        print(f"{b['name']:32} {b['calls']:>11} {cell(b['accuracy'],'.2%'):>9} {cell(b['brier'],'.4f'):>7} "
              f"{b['estimates']:>10} {cell(b['mae'],'.4f'):>8} {cell(b['mape'],'.4%'):>8}")
    for horizon,label,form in ((5,"direction accuracy","+.2%"),(1,"next-close MAE $","+.4f")):
        e=edges[horizon]
        span=f" (approx. 95% range {e['low']:{form}} to {e['high']:{form}})" if e["low"] is not None else ""
        print(f"edge, {label}: logistic - {e['against']} = {e['value']:{form}}{span} over {e['sessions']} sessions: {e['verdict']}")
    print("Same observations for every contender; equal closes count as incorrect for Up and Down.")
    if wide:
        print("QQQ and IWM move closely with SPY: wider style coverage, not independent evidence.")
    print("JSON:",json.dumps({"seconds":round(seconds,1),"symbols":symbols,"board":board,"edge":edges},sort_keys=True))


if __name__=="__main__":
    main()
