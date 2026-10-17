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
