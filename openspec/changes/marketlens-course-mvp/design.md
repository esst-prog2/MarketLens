## Context

See `proposal.md` for motivation and the four capability specs for behavior. The current Python standard-library server serves plain HTML/CSS/JavaScript and a SQLite-backed replay. `core.py` contains fixed allocations and momentum; `service.py` couples the replay cursor, a CSV fingerprint and forecast history. `scripts/download_sample.py` already reads Yahoo chart responses. There is no provider abstraction, trained model, scheduler or schema migration system. Browser learning state is independent localStorage. Existing tests cover arithmetic, replay, malformed input and future-price isolation; browser checks cover the learning journey.

## Goals / Non-Goals

**Goals:** Extend these boundaries with a small local provider/training pipeline, explicit mode isolation, trustworthy timestamps and testable scheduling. Reuse the existing UI and accounting rather than replace them.

**Non-Goals:** No hosted worker, distributed scheduler, user authentication, streaming broker infrastructure or general model platform. Training changes forecasts, not allocation weights or paper holdings. The future-level list remains in the proposal only.

## Decisions

The choices below are assistant-proposed defaults for this reviewable plan. User-confirmed outcomes are recorded in `PLANNING_LOG.md`; these technical defaults do not claim separate user approval.

### 1. Reuse the existing free source behind an adapter

Start with Yahoo chart requests for five-minute observations and daily historical bars through a narrow Python provider interface. Preserve source timestamps and currency; keep fetch time separate. A read-only probe on 2026-09-26 returned 391 non-null five-minute observations per symbol for SPY, IEF and GLD, ending at 2026-09-25 20:00 UTC. No data files were changed by the probe.

This endpoint is unofficial and best-effort. Do not add paid fallback or guarantee future access. Before apply declares live-data work complete, verify fresh responses, session interpretation and permitted local educational usage. If access cannot meet the free-data constraint, report the blocker instead of silently accepting replay-only completion. Avoid building multiple provider integrations in this MVP.

Use a five-minute server refresh interval in regular sessions, bounded HTTP timeouts, exponential backoff for errors, and a shared fetch lock so multiple browser tabs do not multiply calls. Fetch daily history at startup and after a completed session becomes available, not on every quote refresh. Compare observed timestamps with a 30-minute open-session stale threshold; it is not a claimed exchange delay. Outside regular sessions, retain prices as closed-market observations and retry pending completed-bar ingestion on the same bounded refresh cycle. UI polling reads the local cache, not the provider directly.

Alternatives: daily-only data violates the requested intraday behavior; paid services violate the budget; websocket streaming adds unnecessary complexity. Provider terms and actual coverage must be checked independently of a library's software license. The [yfinance project](https://github.com/ranaroussi/yfinance) documents that its Yahoo access is unofficial and intended for personal/research use; that is not a redistribution grant.

### 2. Separate the quote clock from the forecast clock

Quotes can move intraday. Forecasts are issued once per completed daily reference session, targeting the next and fifth subsequent exchange sessions. The UI states the reference and target dates even when the displayed latest quote is newer. Expired or missing-data forecasts stay visible with status and are not described as newly issued.

Use an exchange-calendar dependency for US sessions, holidays, DST and early closes; validate it for these three US-listed instruments. Do not implement 'weekday plus one' or assume 16:00 New York on early-close days. Record UTC timestamps plus exchange session dates. A daily bar is eligible only after its session closes and the provider reports it as completed; absent expected sessions block affected windows rather than shortening a horizon.

Alternative: recomputing predictions every quote refresh would complicate the meaning of 'next-day close', duplicate forecasts and make the demo's accuracy denominator unstable.

### 3. Small trained models with evaluated probabilities

Use scikit-learn for reproducible regularized models rather than invent a percentage formula. Pin tested dependency versions during apply, with NumPy and an exchange-calendar package in a root dependency file. Continue to launch with `python app.py` after documented installation.

Features: trailing 1-, 5- and 20-session returns, trailing 20-session daily volatility and an instrument indicator. All values end at the reference close. Fit preprocessing only on the fitting partition. Use a pooled regularized logistic classifier for the sign of the five-session close change (Up, Down, Flat). Require Up and Down training examples; include Flat when observed. Select the higher estimated probability of Up and Down, with Up as a deterministic tie-break. The probability is for that selected strict direction; Flat outcomes count as incorrect for either. Do not describe Down as 'not Up', which would wrongly treat equal closes as correct.

Calibrate class probabilities using a separate later calibration partition with a sigmoid method supported by the selected library version. If a class is absent, expose sample coverage, do not invent observed examples, and do not claim exact reliability for unseen outcomes. If fitting or calibration cannot produce usable probabilities, publish no new version. Evaluate the selected-direction confidence using Brier error `(confidence - correct)^2` and bins [0,.2), [.2,.4), [.4,.6), [.6,.8), [.8,1], including count and mean confidence versus observed correctness. Label estimates as experimental. The [scikit-learn calibration guide](https://scikit-learn.org/stable/modules/calibration.html) distinguishes classifier output probabilities, calibration and reliability evaluation; merely displaying a percentage is not evidence of calibration.

Use regularized linear regression for next-session return, converted to USD with the reference close. Reject non-finite or non-positive predictions rather than silently clipping them. Compare with a last-close price baseline. Keep the current 20-session momentum direction and always-Up as directional baselines. A trained model need not outperform them to pass; correct measurement is required.

Alternatives: the existing trend-strength score cannot meet the requested probability meaning. Large neural models, parameter searches and generated explanations add scope without helping this small course demonstration. Retain concise template explanations grounded in actual inputs.

### 4. Chronology and enough history before issuing probabilities

Use at least 120 distinct reference sessions for fitting and 40 later reference sessions for calibration, with examples pooled across instruments. End fitting labels before calibration begins, and end calibration labels no later than the issuance cutoff. Purge the full five-session target horizon at boundaries; this also protects the shorter price horizon. Use all eligible labelled examples, including prior mistakes; never fit only incorrect examples.

Fetch multiple years of daily history for current-mode bootstrap. Commit a separate sourced offline history snapshot with at least two years of common sessions so replay has a real warm-up period before the presentation begins. Preserve the original 2024 CSV and legacy replay records. Store dataset provenance and content identity for each model; do not silently apply revised history to old forecasts. Never use today's quotes, full-sample normalization or future rows when replay trains at an earlier date.

The 120/40-session limits are initial engineering minima, not a claim of statistical adequacy. Expose sample counts and keep historical reliability results separate from current-mode results. Overlapping target windows are explicitly disclosed.

### 5. Automatic retraining without an always-on service

Add one in-process background worker, started by `app.py` and stopped cleanly with the server. The cycle ingests observations, evaluates matured forecasts, checks whether the shared completed-session cutoff has advanced, trains eligible models, then issues that cutoff's daily forecasts. Data acquisition/training do not block request handling. A lock prevents concurrent jobs, and a durable unique successful-cutoff key prevents restart duplicates.

On startup, process only the latest eligible current cutoff. Do not backfill imaginary live forecasts for days when the application was not running; historical demonstrations belong in replay. Keep `not enough data`, `running`, `succeeded`, `failed` and retry metadata visible. Publish model artifacts and the active-version pointer atomically only after validation. Preserve the old version on error; failed runs retry with backoff, not a busy loop.

In replay, advancing the simulated daily clock invokes the same pipeline with an injected clock/provider and isolated state. It must not call the live provider. No OS task or hosted service runs when the application is closed. This is the minimum proposed interpretation of automatic retraining, not automatic application restart.

### 6. Fair comparisons use a shared unseen future

For each new version, retain its immediate predecessor. Record shadow predictions from both frozen versions on the next 20 reference sessions after the newer version's training cutoff; neither version may train or calibrate on these comparison observations. Evaluate once their target closes mature, retaining version IDs, reference dates and counts. This provides a finite comparison cohort even when another daily model version becomes active.

Show partial counts while the cohort matures and mark a full cohort complete only after its five-session outcomes arrive. Compare directional accuracy, probability Brier error, next-session MAE/MAPE and the same baseline forecasts. Recent historical fitting or calibration scores are not out-of-sample comparisons. Activate a validated new version without promising improvement; display regression honestly. Automated model selection/rollback based on performance is deferred.

### 7. Extend persistence without conflating modes

Add a schema version and transactional migrations. Proposed entities: observed quotes with provenance; completed daily bars with dataset identity; separate current/replay portfolios and entry snapshots; immutable horizon-specific forecasts; outcomes; model versions; training runs; shadow comparison predictions. Keep symbol, mode, reference session and horizon uniqueness where appropriate. Store trusted locally generated model artifacts under `.runtime/` and a version/config hash in SQLite; never load arbitrary user-uploaded serialized models.

Leave browser learning preferences intact. Preserve `momentum-20-v1` records as heuristic/legacy; do not fabricate probabilities for them. Read-only legacy replay remains inspectable; new trained replay starts an independent experiment against the longer snapshot. Reset acts only on the selected experiment/mode.

For live-mode entries, obtain a complete acceptable quote set before atomically creating fractional holdings. Subsequent valuation can use last-known prices but must label stale/missing components; no automatic trades or rebalancing. Quotes from the most recent completed exchange session are valid closed-market entries and labelled accordingly. Keep original entry timestamp and price per instrument.

### 8. Extend existing API and UI contracts

Keep the current routes and explicit mode context; add typed API state sections for provider status, two forecast targets, reliability and training runs. Add mode switching and a refresh/status control, without triggering provider requests from every UI poll. Preserve learning and strategy routes and their existing limits. Show model version/reference dates in beginner-readable detail panels.

Test the API with deterministic fake providers and clocks, then separately perform a bounded real-source smoke check. UI tests must exercise unavailable/cached prices, mode isolation, both forecasts, automatic replay retraining and saved learning state at desktop and 390px widths. Avoid tests requiring a five-day real wait or an open exchange.

## Risks / Trade-offs

- Free provider availability/terms can change -> isolate the adapter, document usage, show real timestamps and cached failure states; do not call the MVP complete if actual intraday access remains unverified.
- Small datasets and changing markets can produce poor probabilities -> use chronological calibration/evaluation, sample counts and explicit baseline comparisons; no profitability or minimum-accuracy promise.
- Daily retraining adds compute -> tiny regularized models, one worker, bounded cohorts and duplicate-cutoff protection; measure responsiveness during apply.
- Extended history and dependency installation add setup -> commit a sourced demo snapshot and document install/start commands; do not ship local caches, credentials or model binaries in Git.
- Class time cannot wait for outcomes -> deterministic replay exercises the same logic, clearly separated from current prices.
- Missing bars, early closes and historical revisions can distort targets -> calendar validation, provenance, immutable issued forecasts and explicit unavailable/pending outcomes.
- The requested free intraday access plus calibrated forecasts and retraining is larger than the original replay -> retain the existing frontend and limit assets, models and deployment scope strictly.

## Migration Plan

1. Implement against temporary databases and preserve the original CSV/tests; capture a SQLite backup before first real migration.
2. Apply additive schema migration transactionally, classify existing records as legacy replay and leave localStorage keys compatible.
3. Bootstrap complete daily history and model state independently of quote rendering. Until ready, show unavailable-model status rather than fake percentages.
4. Verify both current and replay modes, startup catch-up, automatic training, errors and full class walkthrough. Update README only during apply.
5. On migration failure, roll back the transaction and leave the backup intact; recovery restores the backed-up database with the previous code version. Do not delete user data to make a test pass.
6. Before commit/push, review the diff, keep unrelated exercises unchanged and confirm the assignment repository destination. Submit only after verifying the pushed commit. Archive is optional and outside this proposal step.
