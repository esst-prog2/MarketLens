## Why

The offline replay ends on 2024-12-31, almost two years before the demo, and every measurement covers only SPY, IEF and GLD. Three instruments in one two-year window are thin evidence for a tool whose job is to say whether a model beats the baselines. A read-only probe on 2026-11-03 showed that Yahoo still returns all 753 snapshot closes unchanged. The snapshot can therefore be extended without changing a single past number, including those in the demo text.

## What Changes

- **Fresher replay.** `data/training_prices.csv` runs from 2022-01-03 to 2026-11-02, the last completed session before the download. Practice still starts on 2023-01-03. The first 753 rows stay byte-identical, so the demo path and its numbers are unchanged. The downloader gets a fixed end date, so a re-download reproduces the file.
- **Existing databases keep working.** A replay database created on the shorter snapshot is accepted when the new snapshot's first rows reproduce its stored hash, because every stored record used only those rows. The stored hash is then updated. Any other change of dataset is still refused.
- **Wider measuring universe (harness only).** A separate `data/universe_prices.csv` holds SPY, IEF, GLD, QQQ and IWM over the same sessions. `python scripts/contenders.py --universe` measures all four contenders on it. The logistic contender is fitted on the five instruments, and its output is committed.
- **Instrument lists become a parameter.** The model, the baselines and validation take a symbol list that defaults to the app's three, so the app, its model versions and its screens do not change.
- README, `data/README.md` and the committed contender outputs are updated with the new figures. The HW4 spike output stays as the dated record of the old snapshot.

Not changing: the app's cards, portfolio profiles and model, which stay on three instruments until after the 9 November demo submission (user decision).

## Capabilities

### New Capabilities
- `replay-snapshot`: the bundled replay covers up to a recent completed session, extends without rewriting history, and existing databases survive a pure extension.
- `contender-universe`: contenders can be measured on a wider instrument list than the app shows.

### Modified Capabilities
None (there are no main specs; the unarchived MVP change's market-data requirements still hold: sourced, validated, no gaps filled).

## Impact

- Data: `data/training_prices.csv`, `data/training_sources.json`, new `data/universe_prices.csv` and `data/universe_sources.json`.
- Code: `scripts/download_training_sample.py` (fixed end, optional universe), `marketlens/core.py` (`load_prices` symbols), `marketlens/market_data.py` (`validate_history`/`require_contiguous` symbols), `marketlens/forecasting.py` and `marketlens/contenders.py` (symbols), `marketlens/mvp.py` (extension check), `scripts/contenders.py` (`--universe`).
- Tests: prefix byte-identity of the extended snapshot, the extension acceptance and refusal of other changes, and a five-symbol contender replay. The demo test must stay green unchanged.
- Run time: the full replay grows from 502 to about 960 references, so `scripts/contenders.py` takes about twice as long.
