# MarketLens development notes

Historical milestone notes below describe the original implementation. The current
MVP, installation and demo are documented in README.md and
`openspec/changes/marketlens-course-mvp/`. Future levels are only the proposal list.

## First milestone

The MarketLens README is the main project brief. `casino/` and `snake/` are
separate coding exercises, not parts of this application.

The first implementation is a runnable vertical slice, using Python's
standard library, SQLite and plain HTML/CSS/JavaScript. The interface and
project documentation are in English for the course.

Implemented:

- A validated, sourced 2024 historical price sample for SPY, IEF and GLD.
- Conservative, Balanced and Growth profiles with fixed example weights.
- A user-defined virtual starting balance and fractional-share holdings.
- Daily historical replay, persistent portfolio value and price-only P/L.
- A versioned 20-day momentum baseline with a five-trading-day horizon.
- Immutable forecasts, pending/correct/incorrect results and an always-up
  comparison evaluated on the same observations.
- Explicit historical dates, source details, baseline limitations and a
  heuristic signal-strength label (not an invented confidence probability).

## Guided discovery milestone

The requested direction is a guided learning and investing workspace, beyond
a dashboard of charts. First-time visitors choose a goal (learn, explore or
practice), topics, experience, risk preference and time horizon. Experience
controls the learning path, independently of risk preference. Risk preference
orders fixed educational portfolios; a short horizon highlights risk education
instead of an allocation. Each highlighted mix explains its selection.

Six destinations now connect the experience: For you, Learning library,
Portfolios & strategies, Explore markets, Practice and Model history.
The library has nine internal guides, source links, search, topic filters,
bookmarks and reading completion. Portfolio examples hand their selection to
the existing simulator without overwriting a running portfolio. The strategy
catalog clearly distinguishes the available fixed-holdings simulation from
reading-only contribution/rebalancing concepts and non-trading trend forecasts.

Learning preferences and progress live in browser localStorage. Portfolio and
forecast records remain in SQLite. Changing preferences does not modify holdings;
resetting the replay does not erase reading progress. There is no authentication.

Sources for the educational summaries are linked beside each article:
Investor.gov for risk, allocation, ETFs and regular contributions; FINRA for
bonds; State Street for GLD. The momentum guide describes our own implementation.

The guided flow passed `tests/browser_journey.py` in Edge: required choices,
back navigation, independent experience/risk, all three goal paths, short-horizon
handling, library search/filter/save/read/reload, portfolio handoff and preservation,
forecast evaluation, all six pages at 390px, article dialogs and invalid stored
preferences. No JavaScript errors occurred. All 11 backend tests also passed.

## Verification

- All 11 standard-library tests passed, covering malformed input, portfolio
  arithmetic and persistence, forecast maturity, future-data isolation,
  a complete replay, reset, dataset changes and HTTP behavior.
- Headless Edge checks passed for profile selection, creating a $10,000
  portfolio, six daily steps, evaluated forecasts, reload persistence,
  methodology details and reset. No JavaScript errors occurred.
- Both overview and history fit a 390-pixel mobile viewport without page
  overflow. Desktop and mobile screenshots were saved under `.runtime/`.
