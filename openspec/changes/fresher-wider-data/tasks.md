## 1. Fresher replay

- [x] 1.1 Give `scripts/download_training_sample.py` a fixed end (2026-11-03 00:00 UTC) and a check that refuses to write if any existing close changed
- [x] 1.2 Download; test that the first 753 rows equal the previous snapshot and that the file ends on 2026-11-02 with no gaps
- [x] 1.3 Accept a pure extension in `MVPService`; tests for an older database (accepted, records kept, replay continues past 2024-12-31) and for different data (refused); the demo test stays green unchanged

## 2. Wider universe in the harness

- [x] 2.1 Optional symbol lists for `load_prices`, `validate_history`/`require_contiguous`, `features`/`fit_model`/`predict` and the baselines, default unchanged; test that default model versions are unchanged
- [x] 2.2 Download `data/universe_prices.csv` (SPY, IEF, GLD, QQQ, IWM) with sources; test that its three shared columns equal the replay snapshot
- [x] 2.3 `scripts/contenders.py --universe`; a short five-symbol replay test

## 3. Measure and document

- [x] 3.1 Rerun `scripts/contenders.py` (three instruments, now to 2026-11-02) and `--universe`; commit both outputs
- [x] 3.2 Update README (replay coverage, contenders section) and `data/README.md`; keep the HW4 spike as a dated record
- [x] 3.3 Full suite and both browser workflows; `openspec validate fresher-wider-data --strict`; PLANNING_LOG; commit and push
