## Why

MarketLens already offers guided learning and historical paper investing, but the course MVP now needs fresh intraday prices, meaningful forecast probabilities, next-session price estimates and automatic retraining. This change establishes the first reviewable specification and extends the existing application rather than rebuilding it.

## What Changes

- Keep the English onboarding, nine-guide library, saved reading and three educational allocation profiles.
- Limit the MVP to SPY, IEF and GLD. Fetch actual intraday observations and daily history without paid subscriptions; show source, observation time and freshness. Delayed quotes are acceptable.
- Separate current-data paper investing from the existing historical replay, retaining an explicit offline demonstration path.
- Produce a five-trading-session directional forecast with an estimated probability of that direction being correct, plus a separate next-trading-session closing-price estimate in USD.
- Store forecasts before outcomes, evaluate direction against the fifth-session close and price errors against the next-session close, and compare against simple baselines. Probability reliability is measured, not promised.
- Automatically retrain on newly completed market sessions, keep versioned models and demonstrate how outcomes and new observations enter later training without future-data leakage.
- Preserve existing portfolio records and learning preferences; label old heuristic forecasts separately from trained-model probabilities.

The following are assistant-proposed implementation defaults, not additional user-confirmed requirements: refresh every five minutes while the local server runs; generate forecasts from completed daily closes; check for automatic retraining after each newly ingested complete session and once at startup; no background work while the computer/application is off. Details and failure behavior are in the design and specs.

## Capabilities

### New Capabilities

- `market-data`: Free, timestamped intraday observations, validated daily closes, caching and explicit replay isolation.
- `forecast-evaluation`: Five-session probabilities, next-session price estimates, immutable records and honest outcome metrics.
- `automatic-retraining`: Chronological training, model versioning, automatic triggers and visible run/comparison results.
- `learning-paper-investing`: Preserve the guided learning journey and support reproducible paper portfolios in current-data and replay modes.

### Modified Capabilities

None. There are no existing OpenSpec capability specifications; the application already implements part of this new specification.

## Impact

- Extend `marketlens/core.py`, `marketlens/service.py`, `app.py` and the existing `web/` interface; add provider, forecasting and training modules with focused tests.
- Extend SQLite persistence with migrations and isolate live and replay data. Add pinned Python model/calendar dependencies during apply, retaining one documented startup command after dependency installation.
- Update README startup, model limitations and class-demonstration instructions during apply. Keep `AGENTS.md`, `CLAUDE.md` and the append-only planning log.
- Free Yahoo intraday access is a provisional provider: a read-only probe on 2026-09-26 returned timestamped five-minute bars for all three instruments. This proves present accessibility, not future availability or redistribution rights.
- Before submission, resolve the existing `rkincso/MarketLens` remote versus the assignment's `esst-prog2/<repository>` destination. Do not change remotes or claim submission complete without verifying the destination and successful push.

## Non-goals and Later Levels

No real-money orders, broker connections, actual payments, subscriptions, accounts, public multi-user hosting, tick streaming, extra instruments, news/sentiment, automatic trading, portfolio optimization, dividend/fee/tax accounting, or guaranteed profitable forecasts. Do not change the unrelated `casino/` and `snake/` exercises.

Later levels remain a list only: more instruments and stock search; contribution/rebalancing simulation; richer lessons and learning paths; better models and uncertainty intervals; managed always-on scheduling; accounts and deployment; possible paid product features. Do not write specifications for these levels in this change.

## Class Demonstration

Complete onboarding, read/save a guide, inspect three timestamped current quotes and both forecast types, apply a $10,000 Balanced paper allocation, and show portfolio valuation. Use a clearly labelled deterministic historical replay to reveal next-session and five-session outcomes and an automatic retraining event within the presentation. Show at least one incorrect forecast, both baseline comparisons, and cached-data behavior during a simulated provider failure. Live data retrieval must also have separate verification; offline replay alone does not satisfy the fresh-data requirement.
