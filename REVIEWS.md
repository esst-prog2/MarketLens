# HW6 whole-repository reviews

Each review looks at the whole repository for one kind of problem. Each one, and
what was done about it, is a separate commit on branch `hw6-review`.

## 1. Correctness and look-ahead

**Question:** does any number the program shows use information it could not have
had at that time, or score something against the wrong day?

**Checked, no defect found:**

- `fit_model` (`marketlens/forecasting.py`): the last fitting label ends on the
  session before calibration starts (five-session purge), and the last calibration
  label is the cutoff close itself. No label reaches past the cutoff.
- `features` uses only the 21 closes up to and including the reference session.
- `predict` refuses a model whose cutoff is later than the data it is given.
- Five-session targets come from the XNYS calendar (`target_session`), so holidays
  are skipped; `tests/test_holiday_scoring.py` (HW5) pins this with hand-counted values.
- `track_record` counts only calls whose due session is on or before the new call's
  reference session, so the hit rate shown never includes an outcome not yet known.
- Current mode never issues a forecast whose target close has already happened.
- Version comparisons score both models only on the forecasts they share.

**Defect found and fixed:**

- In current mode the portfolio's start date was the wall-clock UTC date of the
  click (`self.clock().date()`), not the session of the entry prices. HW5 saw it
  as "since Oct 11, 2026" with 2026-10-09 entry prices. It is now the New York
  date of the latest entry quote, the same rule for current and replay mode.
  New test `test_weekend_portfolio_starts_on_its_entry_price_session` was red
  first (`'2023-01-08' != '2023-01-06'`) and is green after the fix; 28 tests pass.

**Noted, not changed:**

- Yahoo stamps a five-minute bar with its start time, so a quote can be up to five
  minutes newer than its `observed_at`. This only makes quotes look older, which
  errs towards "stale", so it is left as is.

## 2. Security

**Question:** what can another web page, a bad provider response or a bad input
make this local server do?

**Checked, no defect found:**

- The server binds only to `127.0.0.1`; static files come from a fixed list, so
  no path can reach outside `web/`.
- POST needs `application/json`, at most 4 KiB, and a matching `Origin` when one
  is sent; a plain cross-site form cannot meet that.
- Every server- or provider-supplied text in the UI (provider errors, training
  errors, model names, timestamps) goes through `escapeHTML`; stored browser
  preferences are validated against fixed lists before use.
- Yahoo responses are capped at 5 MB and checked for symbol, currency, sorted
  unique timestamps and finite positive prices.
- The only SQL built with an f-string (`reset`) uses a fixed list of table names.

**Defect found and fixed:**

- The `Host` header was never checked. With DNS rebinding another site can point
  its own name at 127.0.0.1; its `Origin` then matches `Host`, so it could read
  `/api/state` and call reset. Both GET and POST now answer 403 unless `Host` is
  `127.0.0.1:<port>` or `localhost:<port>`. The new part of `test_api_and_static_files`
  was red first (`HTTPError not raised`) and is green after the fix; 28 tests and
  the `tests/browser_mvp.py` Edge walkthrough pass.

**Noted, not changed:**

- Model artifacts are stored with `pickle` in the SQLite file, and unpickling runs
  code. Only this application writes that file and there is no upload endpoint,
  so whoever can change it can already change the code. Do not open a database
  file from someone else.

## 3. Tests

**Question:** would the tests go red if the code that produces the project's
headline numbers were wrong?

**Method:** `scripts/mutation_check.py` breaks one important line at a time
(twelve of them: baselines, Brier, confidence bins, the purge, the track record,
live backfilling, staleness, Flat outcomes, the quote cache, the ridge fit, the
allocation), runs the whole unit suite, and restores the file. A break the suite
does not notice marks a missing test. Output: `scripts/mutation_check_output.txt`.

**Found:** 6 of 12 breaks went unnoticed with all 28 tests green:

- always-up and momentum baselines scoring the model's call instead of the outcome
  (no test checked their values);
- the track record counting calls issued earlier but not yet due (no such call
  in the test data);
- confidence bins rounding instead of flooring (the test only used exact bin edges,
  where both give the same bin);
- Brier using absolute instead of squared error (the test's only error was 1, and 1² = 1);
- current mode issuing a forecast whose outcome is already known (no test).

These are exactly the functions behind the HW4 result (accuracy against the
baselines, Brier, bins), so the project's main finding had no protection.

**Fixed:**

- `test_baselines_brier_and_bins_counted_by_hand`: three calls where the model's
  call and the outcome differ; always-up 2/3, momentum 3/3, Brier 0.3202 and bin
  counts [0, 0, 2, 1, 0] were counted by hand.
- `test_track_record_uses_only_earlier_calls_in_same_bin` now also holds 40 calls
  issued before but due after the new call; the count must stay 30.
- `test_lagging_history_never_backfills_a_known_live_outcome`: daily bars stop at
  2022-12-28 on 2023-01-04; only the five-session calls (due 2023-01-05) may be issued.

Rerun: all six are now caught; 30 tests pass.

**Noted, not changed:**

- The two browser walkthroughs (`tests/browser_*.py`) are scripts, not part of
  `unittest discover`; they need Playwright and Edge and are run by hand.
- The mutation check takes about 1.5 minutes per mutation, so it is a review tool,
  not part of the regular test run.

## 4. Simplification and dead code

**Question:** what code is never used, repeated, or more complicated than needed?

**Method:** an AST scan of every tracked Python file for imports and top-level
functions or methods whose name appears nowhere else (Python and JavaScript),
plus reading `marketlens/` and `web/` for repeated logic.

**Removed or simplified:**

- Unused imports: `Service` in `app.py`, `calendar` in `marketlens/mvp.py`,
  `Request` in `tests/test_mvp.py`.
- `MVPService.refresh(force=False)`: `force` was never read or passed.
- The rule "a quote is usable if it is current, closed or replay" was written out
  three times in `marketlens/mvp.py`, twice as the identical all-three-symbols
  check (portfolio entry and `can_invest`). It is now `USABLE` and `usable(quotes)`,
  so entry and the button can no longer disagree.

30 tests pass; no behaviour changed.

**Checked and kept:**

- `marketlens/service.py`, `data/prices.csv`, `web/app.js`'s legacy branch and
  `scripts/download_sample.py` look old but still serve the read-only "Legacy 2024
  replay" mode and the migration test.
- `legacy_snapshot` builds the old `Service` with `object.__new__` to skip its
  table setup; odd, but it avoids writing to a legacy database while reading it.
- `NoNetwork` is repeated in `scripts/spike_replay.py` and
  `tests/test_holiday_scoring.py`; five lines each, kept so each file stands alone.
