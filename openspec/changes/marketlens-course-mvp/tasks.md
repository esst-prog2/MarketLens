## 1. Dependencies, data source and reproducible inputs

- [x] 1.1 Add pinned model and exchange-calendar dependencies and installation instructions; verify installation in an isolated environment and that `python app.py` remains the documented startup command.
- [x] 1.2 Add a narrow free Yahoo provider adapter using the existing downloader's response format, bounded timeouts and normalized source metadata; verify valid intraday and daily responses for SPY, IEF and GLD with fixtures and a separate real-source smoke check, and document source usage constraints.
- [x] 1.3 Validate session calendars, UTC/exchange dates, finite positive USD prices and expected completed sessions; verify holiday, DST, early-close, duplicate, missing-bar and provisional-bar cases using deterministic inputs.
- [x] 1.4 Add a separate sourced offline history snapshot with at least two years of common sessions and recorded provenance; verify it supports the specified fitting/calibration warm-up plus a version-comparison demonstration without changing the original 2024 sample.

## 2. Persistence and market refresh

- [x] 2.1 Add transactional schema-versioned migrations, a pre-migration backup and separate current/replay/legacy records; verify migration preserves an existing portfolio, heuristic forecasts and browser preferences and that failure rolls back safely.
- [x] 2.2 Persist normalized quotes, completed bars, their timestamps and source/data identities; verify duplicates are idempotent and invalid observations cannot replace usable data or enter forecast windows.
- [x] 2.3 Implement one bounded background refresh worker with startup refresh, five-minute session polling, fetch locking and error backoff; verify with a fake clock/provider that multiple browser requests do not multiply upstream calls and the server remains responsive.
- [x] 2.4 Expose current, stale, closed-market, unavailable and provider-failure states; verify the 30-minute open-session rule, unchanged old quotes, closed sessions and cached-data behavior without silent replay fallback.

## 3. Forecast fitting and probability meaning

- [x] 3.1 Build trailing-return/volatility/instrument features and one-/five-session targets; verify feature cutoffs, holiday targets and exclusion of incomplete horizons or missing expected sessions.
- [x] 3.2 Implement chronological fit/calibration partitions with at least 120 fitting and 40 calibration reference sessions and five-session boundary purging; verify preprocessing and labels cannot use observations past their cutoff.
- [x] 3.3 Fit the regularized directional classifier with separate sigmoid probability calibration, including explicit handling of missing classes; verify valid selected-direction probabilities, Flat outcomes and unavailable-model behavior rather than relabelled heuristic strength.
- [x] 3.4 Fit the regularized next-session return regressor and convert to a positive USD closing-price estimate; verify the separate target/date, last-close baseline and rejection of invalid model outputs.
- [x] 3.5 Persist complete model versions with configuration, data identity and fit/calibration ranges; verify deterministic results from identical inputs and that future-data perturbations do not change earlier model outputs.

## 4. Issuance, outcomes and model comparisons

- [x] 4.1 Store immutable horizon-specific daily forecasts with actual issuance time, reference close, target session, model version and mode; verify refresh/retraining/restart does not duplicate or overwrite forecasts and no target already known at issuance is counted as a live prediction.
- [x] 4.2 Evaluate matured direction and price outcomes with pending handling, dollar error, percentage error, accuracy, MAE and MAPE; verify equal-close direction handling, the $100 versus $102 example and exclusion of pending records from aggregates.
- [x] 4.3 Record always-Up, momentum and last-close baselines on the same forecast observations; verify benchmark alignment and visibility when a baseline wins.
- [x] 4.4 Add selected-direction Brier error and confidence-bin reliability summaries with sample counts; verify bin endpoints, no-outcome states, separation by mode/version and disclosure of overlapping targets.
- [x] 4.5 Record shadow predictions from consecutive frozen versions over a shared 20-reference-session future cohort; verify both versions excluded comparison outcomes from training/calibration and that the UI can show pending, partial, complete and worse-new-version results.

## 5. Automatic retraining and recovery

- [x] 5.1 Trigger fitting automatically on each new eligible completed shared session and at startup; verify newly available labels are included, duplicate successful cutoffs are skipped and startup catches up without inventing missed live forecasts.
- [x] 5.2 Implement durable run states, mutual exclusion, atomic model activation and bounded retry; verify interrupted/failed/insufficient-data runs retain the previous usable version and record a visible reason.
- [x] 5.3 Run the same training and evaluation pipeline against an injected replay clock/provider; verify replay advances trigger actual retraining and outcome evaluation while network access is disabled and live records remain untouched.

## 6. Guided UI and paper portfolio integration

- [x] 6.1 Extend API/UI state with explicit current-data versus replay selection, quote provenance and two distinct forecast cards per instrument; verify reference/target dates, probability wording, missing-model states and independent intraday quote updates.
- [x] 6.2 Support current-data paper entry using all three acceptable quotes and stored entry snapshots while retaining the fixed profiles and virtual balance bounds; verify $10,000 Balanced arithmetic, rejection of stale/missing entry data and clear partial-cache valuation timestamps.
- [x] 6.3 Add training status and version/baseline/reliability comparisons to Model history; verify a new model does not change old predictions, portfolio holdings or browser learning selections.
- [x] 6.4 Preserve onboarding, nine guides, search, bookmarks and strategy limitations while updating obsolete model descriptions; verify the existing guided browser journey, independent resets and all new views at desktop and 390px widths.

## 7. Course demonstration and delivery verification

- [x] 7.1 Run the full deterministic backend/API/browser regression suite, covering migration, provider outages, no-look-ahead behavior, scheduling and mode isolation; record actual results and keep unrelated casino/snake files unchanged.
- [x] 7.2 Walk through the proposal's class demo using live-source verification and explicit offline replay, including an incorrect forecast and an automatic retraining comparison; verify the demo works outside market hours and uses no paid credentials.
- [x] 7.3 Update README with install/start commands, provider/model limitations and the demonstration sequence; verify instructions on a clean environment and retain later levels only as the proposal's list.
- [x] 7.4 Validate the completed change with `openspec validate marketlens-course-mvp --strict`, review code against every scenario and append implementation decisions to the planning log; verify no requirement is marked complete merely because its artifact exists.
- [x] 7.5 Resolve the assignment repository destination with the user before changing remotes, review the staged file list, commit the scoped MVP/spec/log files and push to the authorized course repository; verify the remote commit hash and report the submission URL. Do not include local databases, installed tools, caches, model binaries or unrelated exercises accidentally.

## Apply verification ? 2026-09-26

25 deterministic backend/API tests passed. The legacy guided browser regression and the new offline MVP browser walkthrough passed, including 26 replay advances, a complete frozen-model cohort, errors, outage/cache handling, learning-state preservation and 390px layouts. Real Yahoo retrieval succeeded for all three symbols; 1,255 common daily sessions through 2026-09-25 supported successful current-model training. Pinned packages installed in a fresh venv, pip check passed, documented CLI startup served trained replay, and strict OpenSpec validation passed. GitHub API confirms esst-prog2/MarketLens is not a fork.

Delivery verified: commit `3fca6c3c878bbfb6230ae9fcd0d3088b55b3ee14` reached `esst-prog2/MarketLens` main; local and remote hashes matched. Submission URL: https://github.com/esst-prog2/MarketLens.
