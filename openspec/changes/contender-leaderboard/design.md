## Context

`marketlens/contenders.py` (pushed on branch `contenders`) gives always-up, momentum, last-close and the logistic model one `fit(rows)` / `predict(rows)` interface, plus `leaderboard()` on shared observations. The app computes baselines differently: `forecasting.metrics()` derives them from fields on the model's own stored records. This change makes the app use the contender interface and shows the result on Model history.

## Goals / Non-Goals

**Goals:** one scoring path for screen and script; honest uncertainty; visible change over time; no schema migration.

**Non-Goals:** new models, accounts or a public leaderboard, changes to training or portfolios, removing the existing metric cards (they stay for the main model).

## Decisions

- **Store baselines as records, do not recompute them.** In `MVPService._issue`, after the model's records, call each baseline's `predict(rows)` and insert its records with `series = model = <contender name>`. The insert goes through the same no-backfill check and `INSERT OR IGNORE`. The table already allows this: it is unique on `(mode, series, model, symbol, reference, horizon)`, and the `main_forecast` index covers only `series='main'`. *Alternative:* recompute at snapshot time from history. Rejected because it would not be an issued record, and current mode could not prove issuance time. Numerai likewise treats benchmark predictions as submissions.
- **Reuse `leaderboard()`.** The snapshot loads the main series plus each contender series, evaluates them, and passes `{name: records}` to the same function the script uses.
- **Edge as a block-paired difference.** For each shared reference session, average the per-symbol difference (model correct − baseline correct; or model error − last-close error). Group consecutive reference sessions into blocks of 5 and take block means. The edge is their mean, and the range is ±1.96·sd/√blocks. "Best baseline" means the one with the highest accuracy on the shared observations (ties go to always-up). A minimum of 30 sessions (6 blocks) matches the existing 30-call rule for the hit rate. *Alternative:* a bootstrap. Rejected for now because a block standard error is explainable in one sentence and deterministic.
- **Rolling chart.** Server-side: per contender, a list of `{date, accuracy}` over a trailing window of 20 shared references. Client-side: one inline SVG with fixed y-axis 0–100%, a dashed 50% line and a legend, colour-coded per contender. The existing `chart()` helper scales y to the data, which would exaggerate small differences, so the chart gets a small dedicated function.
- **Script parity.** `scripts/contenders.py` prints the edge lines from the same function. A test checks that the snapshot leaderboard equals `leaderboard(replay(...))` over a short replay.

## Risks / Trade-offs

- [Pre-upgrade databases lack contender records] → shared observations start at the upgrade; the table shows its call counts. A fresh `--database` gives the full history.
- [Five-session blocks still understate dependence across the three symbols] → the range is labelled "approximate", and the verdict only uses clear exclusions of zero.
- [Snapshot cost grows with four series] → measured against the 0.7 s/step replay budget; if it is noticeably slower, cache per cursor.
