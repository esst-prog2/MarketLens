"""HW4 spike: one full headless walk-forward replay. python scripts/spike_replay.py"""
import json
from pathlib import Path
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from marketlens.mvp import MVPService


class NoNetwork:
    """Replay never needs the provider; fail loudly if anything tries to use it."""
    name="offline spike"
    def __getattr__(self,name):
        raise RuntimeError("Replay must not touch the network.")


def main():
    with tempfile.TemporaryDirectory() as folder:
        started=time.perf_counter()
        service=MVPService(ROOT/"data/training_prices.csv",Path(folder)/"spike.sqlite3",NoNetwork())
        steps=0
        while True:
            try:
                service.advance("replay")
            except ValueError:  # End of the historical sample.
                break
            steps+=1
        seconds=time.perf_counter()-started
        m=service.snapshot("replay")["performance"]
    print(f"steps: {steps}  seconds: {seconds:.1f}  seconds/step: {seconds/steps:.3f}")
    print(f"evaluated 5-day calls: {m['evaluated']}  next-day prices: {m['price_evaluated']}  pending: {m['pending']}")
    print(f"accuracy {m['accuracy']:.4f}  always-up {m['always_up']:.4f}  momentum {m['momentum']:.4f}")
    print(f"brier {m['brier']:.4f}  (constant 0.5 answer scores 0.2500)")
    print(f"next-day MAE ${m['mae']:.4f}  last-close MAE ${m['last_close_mae']:.4f}  MAPE {m['mape']:.4%}")
    print("confidence bins (stated confidence -> delivered accuracy):")
    for b in m["bins"]:
        if b["count"]:
            print(f"  [{b['low']:.1f},{b['high']:.1f})  n={b['count']:4d}  stated {b['confidence']:.3f}  delivered {b['accuracy']:.3f}")
    print("JSON:",json.dumps({"steps":steps,"seconds":round(seconds,1),**{k:v for k,v in m.items() if k!="bins"},"bins":m["bins"]},sort_keys=True))


if __name__=="__main__":
    main()
