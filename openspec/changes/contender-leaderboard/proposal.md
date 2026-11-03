## Why

MarketLens is a tool that measures whether a model beats simple baselines, but the side-by-side comparison of contenders only exists in a terminal script (`scripts/contenders.py`). The screen still centres on one model. Similar products put the comparison in front of the user: Numerai shows a leaderboard, publishes benchmark models that everyone is scored against, and scores a model by what it adds beyond those benchmarks. Its score charts also show that results change over time. The final demo on 1 December 2026 is scored by the audience on what the program shows, so the comparison belongs on screen.

## What Changes

- **Leaderboard on Model history.** Always-up, 20-session momentum, last-close and the logistic model appear in one table, scored only on the observations they all answered. The table updates after every **Next trading day** in replay and every new session in current mode.
- **Baselines become stored contenders.** At each issuance, every contender's forecasts are stored as immutable records next to the model's, through the existing contender interface. Today the baselines are recomputed from the model's own records.
- **Edge over the best baseline, with uncertainty.** Two lines under the table. The first gives the model's direction accuracy minus the best baseline's, with an approximate 95% range, and a verdict: *better*, *worse* or *no measurable difference*. The second does the same for next-close error against last-close. It shows "not enough history yet" until 30 shared reference sessions exist.
- **Rolling accuracy chart.** One line per direction contender: accuracy over the latest 20 shared reference sessions, by reference date.
- `scripts/contenders.py` prints the same edge lines, so the terminal and the screen use one calculation.

Not changing: forecasts, model training, the portfolio, current/replay isolation, the version comparisons, the existing metric cards.

## Capabilities

### New Capabilities
- `contender-leaderboard`: contenders' forecasts are stored and scored side by side on shared observations, and their difference is shown with its uncertainty and over time.

### Modified Capabilities
None. There are no main specs yet (the MVP change was never archived). This adds to the MVP's *Baseline comparisons* behaviour without changing it: the existing baseline figures stay.

## Impact

- `marketlens/contenders.py`: an edge calculation and rolling accuracy.
- `marketlens/mvp.py`: store contender records when issuing, and add a `contenders` block to the snapshot.
- `web/mvp.js`, `web/index.html`, `web/style.css`: the table, the edge lines and the chart on Model history.
- Tests: hand-counted edge and rolling values; leaderboard equals `scripts/contenders.py` on the same replay; no contender record is backfilled in current mode.
- No schema migration: the existing `m_forecasts.series` column holds the contender name. Databases created before this change get contender records only from the first session after upgrading. Until then the shared observations, and so the table, start small.
- README section 1 (the demo) will name the leaderboard; that wording is decided in `revise-demo-description`.
