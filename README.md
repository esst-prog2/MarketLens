# MarketLens
A local course MVP for guided market learning, calibrated forecasts and paper portfolios.

## Install and run

Tested on Windows with **Python 3.13.2**. Use Python 3.13 and the pinned packages:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\Activate.ps1
python app.py
```

If PowerShell blocks activation, run `.\.venv\Scripts\python app.py` directly.
On macOS/Linux use `source .venv/bin/activate` after creating the environment.
Open http://127.0.0.1:8080. Stop with Ctrl+C. Optional flags:
`python app.py --no-browser --port 8081 --database .runtime/demo.sqlite3`.
Node/OpenSpec are development tools; the application does not need them at runtime.

Current mode attempts free Yahoo Finance retrieval in a background worker. No paid
credentials are needed. Dependencies need downloading once; **Historical replay**
then works without internet. The server binds only to this computer. It is a shared
local workspace, with no accounts, payments or real orders.

## What the MVP does

Choose a learning goal, topics, experience, risk preference and horizon. Browse nine
searchable guides, save reading and compare three fixed educational allocations.
Preferences and reading progress stay in browser localStorage; changing them never
changes existing holdings. The English interface includes six connected views.

Select a data mode above the tabs:

- **Current market data:** SPY, IEF and GLD five-minute observations, each with source,
  observation/fetch timestamps and current/stale/closed/unavailable state. Provider
  delay is unknown. Polling every five minutes is not guaranteed data latency.
  Quotes older than 30 minutes during an open session are stale. Failures retain
  original cached timestamps with an error; they never switch to replay.
- **Historical replay:** a sourced 753-session 2022?2024 snapshot; 2022 is warm-up,
  practice starts on 2023-01-03. Each Next trading day runs the same actual training,
  issuance and evaluation pipeline against a simulated clock, with no network calls.
- **Legacy 2024 replay:** read-only inspection of an existing original experiment.
  Its momentum strength remains a heuristic, never a calibrated probability.

Each instrument shows a **five-trading-session Up/Down call** and a separate
**next-session USD closing-price estimate**, reference/target dates and model version.
The headline for the Up/Down call is the **measured hit rate** of earlier evaluated
calls in the same 0.2-wide confidence band, shown once at least 30 such calls exist.
The model's own estimate appears only in small print, labelled uncalibrated (see
*Spike: full replay* below for why).
Intraday quotes do not rewrite these daily forecasts. Exchange sessions account for
holidays, daylight saving and early closes. The adapter conservatively excludes
same-exchange-date daily bars, even after close, because they can be provisional.

The model uses trailing 1/5/20-session returns, 20-session volatility and instrument
identity. Logistic classification and ridge return regression fit only past labels.
At least 120 fitting sessions precede 40 calibration sessions, with a five-session
purge. Preprocessing fits only the fitting partition. Sigmoid calibration uses
scikit-learn 1.9.1's pinned Platt implementation, explicitly aligned to fitted
classes (including Flat); its internal `_SigmoidCalibration` API is covered by tests
and must be rechecked before a dependency upgrade. Missing Up/Down coverage or a
new calibration class blocks activation. A fitted Flat class with no calibration
examples uses sigmoid target smoothing, not fabricated observations; counts are
shown and reliability for rare/unseen outcomes is unproven. See the
[calibration guide](https://scikit-learn.org/stable/modules/calibration.html).

Automatic retraining runs on new eligible shared daily history while the server is
open. Startup catches up only to the latest cutoff, without inventing missed live
forecasts. Failed or interrupted runs retain the previous usable model and a visible
reason. No scheduled work runs while the app/computer is off. This is automatic
**model retraining**, not an operating-system restart service.

Model history keeps mistakes, pending outcomes, model IDs and actual issuance times.
Equal five-session closes count as incorrect for either strict direction. A $100
price estimate versus an actual $102 close has $2 error and 1.9608% percentage error.
It reports accuracy, MAE, MAPE, selected-direction Brier error and five reliability
bins with counts. Always-Up, 20-session momentum and last-close baselines use the
same observations. Consecutive frozen versions are also compared on their shared
next 20 reference sessions, with pending/partial/complete status. Newer can be worse;
overlapping targets are not independent. No accuracy or profit guarantee is made.

Paper portfolios accept $100?$1,000,000 and fixed fractional holdings. Current-mode
entry requires all three usable quotes; the most recent completed session is valid
while the market is closed. Subsequent cached/partial valuations identify each
component's timestamp. There are no distributions, fees, taxes, slippage, contributions
or executed rebalancing. Current and replay portfolios and resets are independent.

## Class demonstration

1. Start the app; complete onboarding and save/read a guide. Show the library and
   educational reasons for the Balanced example.
2. In Current market data, inspect all three quote timestamps/source/freshness and
   both forecast targets in Practice. Outside exchange hours the quotes say closed.
   Initial history/model bootstrap can take several seconds. Apply Balanced $10,000.
3. Explicitly select Historical replay. Apply a separate Balanced $10,000 portfolio.
   Advance once: prices/P&L change, the first price errors mature and training runs
   automatically. Advance five sessions to show correct and incorrect direction calls.
4. Advance **26 sessions in total** from the initial replay date. Open Model history:
   inspect errors, baselines, reliability, training runs and a complete frozen-version
   comparison. Show both improvements and regressions, without changing old forecasts.
5. Show failure behavior using `python tests/browser_mvp.py`: its explicitly fake
   provider produces a quote update and then an outage. It asserts cached values,
   stale timestamps, independent resets and the same offline replay demonstration.
   These fixtures are not claimed as proof of real-source access.
6. Separately run `python scripts/smoke_market_data.py` for actual free intraday and
   daily retrieval for all three symbols. An outage is reported, never hidden.

## Verification and persistence

```powershell
python -m unittest discover -s tests -p "test*.py" -v
python -m pip install playwright==1.58.0
python tests/browser_journey.py
python tests/browser_mvp.py
python scripts/smoke_market_data.py
openspec validate marketlens-course-mvp --strict
```

Browser checks use installed Microsoft Edge, isolated browser state and temporary
databases; they do not modify your portfolio. Screenshots go under `.runtime/`.
On 2026-09-26, real-source checks retrieved all three intraday observations and 1,255
common completed sessions through 2026-09-25; current-model training succeeded.
All 25 deterministic backend/API tests and both browser workflows passed.
The deterministic tests separately cover calendars, chronology, calibration,
migration rollback, worker responsiveness, cache failures, metrics and mode isolation.

SQLite/model artifacts live under ignored `.runtime/`. Before the first additive
migration, an existing database is backed up as `marketlens.sqlite3.pre-mvp.bak`.
Legacy records and browser keys are preserved. A failed migration rolls back; retain
the backup. For recovery stop the app, preserve the failed database separately and
restore the backup with the previous application version. Never overwrite a backup
just to retry. For a fresh independent demo choose a new `--database` filename.

Yahoo's chart endpoint is unofficial, best effort and may reject access. This is a
personal educational integration, not a licensed commercial data feed. Retrieval
success does not grant redistribution or commercial-use rights; review the
[provider's terms](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html) before
any other use. See [data provenance](data/README.md) for exact sources and identities.

The MVP change, specs and task checklist are in
[openspec/changes/marketlens-course-mvp](openspec/changes/marketlens-course-mvp/).
Later levels remain only the list in its proposal. Decisions are append-only in
[PLANNING_LOG.md](PLANNING_LOG.md).
## Spike: full replay

`python scripts/spike_replay.py` runs the whole 753-session snapshot headlessly
(501 walk-forward steps, retraining at each cutoff, temporary database, no network)
and prints the metrics. Committed output: [scripts/spike_replay_output.txt](scripts/spike_replay_output.txt).
Measured on 2026-10-03: 348.7 s (0.696 s/step); 1,491 evaluated five-session calls,
accuracy 52.3% vs always-Up 54.8% and momentum 51.8%; Brier 0.266, worse than a
constant 0.5 (0.250); next-session MAE $1.586 vs last-close $1.584. Confidence bands
promise 55/67/85% and deliver 52/52/55% (n = 755/678/58). The model has no measured
edge, so its confidence is not presented as a probability.

The original course brief follows.

## 1. THE DEMO
I open MarketLens in the browser as a beginner investor with little knowledge of financial markets and select the Balanced profile with a virtual starting balance of $10,000. The dashboard shows current market views for US Equities, US Government Bonds, and Gold, each with a forecast direction, confidence score, risk level, and a short explanation written for non-expert users. I apply the suggested model allocation to the virtual portfolio, which is then tracked using real market prices and shows how much the simulated investment gains or loses over time. I open Model History and compare earlier forecasts with actual market outcomes, including incorrect predictions. The system stores these forecast errors and uses them during periodic model retraining so that later model versions can be evaluated against earlier ones.

## 2. The shape

in     continuously updated real-world market data for US equities,
       US government bonds, and gold; a selected investor profile
       and a user-defined virtual starting balance

out    a simulated portfolio allocation, forecast signals with confidence scores,
       and continuously tracked virtual profit or loss based on actual market prices

on screen   the user chooses a risk profile and enters how much virtual money
            to invest, reviews simplified market signals and explanations,
            applies a suggested allocation to the virtual portfolio, and watches
            the portfolio change as new market data arrives. The user can later
            compare earlier forecasts with the actual market outcome.

## 3. The size

### First useful version

- The user selects a beginner investor profile and enters a virtual starting balance.
- MarketLens uses real-world market data for US equities, US government bonds, and gold.
- The system produces forecast signals with confidence scores and simple explanations.
- The user can apply a suggested model allocation to a virtual portfolio.
- The portfolio is tracked using updated real market prices and shows simulated profit or loss.
- Previous forecasts are stored and compared with actual market outcomes.
- The system measures forecast performance and supports periodic model retraining based on past prediction errors.

### Not this term

- Trading with real money.
- Connecting to brokerage accounts.
- Automatically executing real trades.
- Paid subscriptions or payment processing.
- Regulated personalized investment advice.
- Full options and futures trading.
- High-frequency or tick-by-tick real-time market data.
- Support for every global market and asset class.

## 4. How we would know it works

- Given incomplete or malformed market data, the system does not create a forecast and reports which required data is missing.
- Given a stored forecast and the corresponding later market data, the system calculates whether the forecast direction was correct and updates the model performance statistics.
- Given a virtual portfolio and a new market price, the displayed portfolio value and profit or loss change consistently with that price movement.

## 5. What could stop this

- Reliable and affordable market data may be limited. Some providers offer delayed data or restrict real-time access, so the first version may use continuously updated but not tick-by-tick market prices.
- Building a forecasting model that performs better than simple baselines may be difficult. The project still works if the model's limitations are measured honestly and displayed to the user.
- News and macroeconomic data can be difficult to collect consistently and may introduce noise, so these may be added only after the core price-based forecasting system works.
- The model must avoid look-ahead bias: when evaluating a historical prediction, it must only use information that would have been available at the time of that prediction.
- Financial markets change over time, so a model that works well on historical data may perform worse in new market conditions. Performance therefore has to be tracked continuously.
- The project will not use real customer money or connect to brokerage accounts during the course, so there is no need to store real banking or brokerage credentials.

### Data

The project will use publicly available or API-provided historical and current market data for equities, government bonds, and gold. The data will consist of market prices, volumes, and related financial indicators rather than personal or sensitive user information. A small sample dataset will be stored in the repository so the application can be demonstrated in class even if an external data provider is temporarily unavailable.

