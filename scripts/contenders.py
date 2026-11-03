"""All contenders side by side on the full snapshot replay. python scripts/contenders.py"""
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from marketlens.contenders import CONTENDERS, leaderboard, replay
from marketlens.core import load_prices
from marketlens.mvp import MVPService


def cell(value, form):
    return "—" if value is None else format(value, form)


def main():
    rows=load_prices(ROOT/"data/training_prices.csv")
    start=MVPService.replay_start  # Same first practice session as Historical replay.
    started=time.perf_counter()
    board=leaderboard(replay([c() for c in CONTENDERS],rows,start))
    seconds=time.perf_counter()-started
    print(f"sessions {rows[start]['date']}..{rows[-1]['date']}  references: {len(rows)-start}  seconds: {seconds:.1f}")
    print(f"{'contender':32} {'5-day calls':>11} {'accuracy':>9} {'brier':>7} {'1-day est.':>10} {'MAE $':>8} {'MAPE':>8}")
    for b in board:
        print(f"{b['name']:32} {b['calls']:>11} {cell(b['accuracy'],'.2%'):>9} {cell(b['brier'],'.4f'):>7} "
              f"{b['estimates']:>10} {cell(b['mae'],'.4f'):>8} {cell(b['mape'],'.4%'):>8}")
    print("Same observations for every contender; equal closes count as incorrect for Up and Down.")
    print("JSON:",json.dumps({"seconds":round(seconds,1),"board":board},sort_keys=True))


if __name__=="__main__":
    main()
