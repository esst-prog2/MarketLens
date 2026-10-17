"""HW6 test review: break one line at a time and check that the unit tests notice.

python scripts/mutation_check.py [mutation name ...]   (restores every file)
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MUTATIONS = [
    ("always-up baseline scores the model's call", "marketlens/forecasting.py",
     '"always_up": mean([r["actual"] == "Up"', '"always_up": mean([r["direction"] == "Up"'),
    ("momentum baseline scores the model's call", "marketlens/forecasting.py",
     '"momentum": mean([r["actual"] == r["momentum"]', '"momentum": mean([r["direction"] == r["momentum"]'),
    ("no purge between fitting and calibration", "marketlens/forecasting.py",
     'fit_end = cal_start - CONFIG["purge"] - 1', 'fit_end = cal_start - 1'),
    ("track record counts calls not yet due", "marketlens/forecasting.py",
     'r["due"] <= record["date"]', 'r["date"] < record["date"]'),
    ("confidence bin rounds instead of floors", "marketlens/forecasting.py",
     'return min(4, int(confidence*5))', 'return min(4, round(confidence*5))'),
    ("Brier uses absolute instead of squared error", "marketlens/forecasting.py",
     '(r["confidence"]-r["correct"])**2', 'abs(r["confidence"]-r["correct"])'),
    ("live mode backfills already-known outcomes", "marketlens/mvp.py",
     'if mode == "current" and close_time(record["due"]) <= now:', 'if False:'),
    ("stale threshold 60 instead of 30 minutes", "marketlens/market_data.py",
     'timedelta(minutes=30) else "stale"', 'timedelta(minutes=60) else "stale"'),
    ("equal closes count as Up", "marketlens/core.py",
     'return "Up" if change > 0', 'return "Up" if change >= 0'),
    ("older quote may replace newer cached quote", "marketlens/mvp.py",
     '> timestamp(quote["observed_at"]):', '< timestamp(quote["observed_at"]):'),
    ("ridge fitted on calibration examples too", "marketlens/forecasting.py",
     'regressor.fit(x, r)', 'regressor.fit(np.vstack((x, cx)), np.concatenate((r, examples(cal_indices)[2])))'),
    ("portfolio uses a fixed 50/50 split", "marketlens/core.py",
     'balance * weight / prices[symbol]', 'balance * 0.5 / prices[symbol]'),
]

ONLY = set(sys.argv[1:])
for name, file, old, new in MUTATIONS:
    if ONLY and name not in ONLY:
        continue
    path = ROOT / file
    original = path.read_bytes()
    text = original.decode()
    assert text.count(old) == 1, (name, text.count(old))
    try:
        path.write_bytes(text.replace(old, new).encode())
        result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                                cwd=ROOT, capture_output=True, text=True)
        last = (result.stdout + result.stderr).strip().splitlines()[-1]
        print(f"{'caught ' if result.returncode else 'MISSED '} {name}  [{file}]  {last}", flush=True)
    finally:
        path.write_bytes(original)
