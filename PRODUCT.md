# Product

<!-- impeccable:product-schema 1 -->

> Written by Impeccable `init` on 2026-11-14 without a live interview: the user asked for this step to run while they were away. Every fact below comes from the approved design doc (`designs/promo-page.md`), the README, PLANNING_LOG.md or the code. Lines marked *(inferred)* are assumptions to confirm.

## Platform

web

## Stack

Promo page: plain static HTML/CSS with a little vanilla JavaScript, served by GitHub Pages from `docs/` (delegated: the user left the build to the assistant; static matches the existing `web/` code and needs no build step on Pages). The app itself is Python 3.13 + SQLite + vanilla HTML/JS, run locally.

## Users

- **The course audience** (classmates, the instructor, and strangers who open the page): they judge a student project in a few minutes, on a laptop or phone, and score the program, not the slides.
- **Beginner investors** (the app's stated user since the first-week brief): people with little market knowledge who meet confident forecasts and do not know how to judge them.

## Product Purpose

MarketLens is a measuring tool for forecasts. It stores every forecast before its outcome exists, never rewrites it, and scores every contender (always up, 20-session momentum, last-close and the student's own calibrated logistic model) on the same observations. Success is an honest answer to "does this forecast beat the simplest guess?", including when the answer is no.

## Positioning

Most finance tools sell an edge. MarketLens measures whether one exists and says so plainly. Its own trained model is just one contender, and on 2,871 five-session calls (SPY, IEF, GLD, 2023-01-03 to 2026-11-02) the verdict is "no measurable difference" against always up. The bar is the simplest guess, not a coin flip.

## Operating Context

- Runs locally (`python app.py`, http://127.0.0.1:8080) with a current-data mode (free Yahoo quotes) and an offline Historical replay of 1,213 real sessions.
- Model history shows the contenders side by side, the edge with an approximate 95% range and verdict, and a 20-session rolling accuracy chart.
- Course context: Advanced Programming, Corvinus University of Budapest; final demo on 1 December 2026 as a five-minute screenshot presentation.

## Capabilities and Constraints

- Five-session Up/Down calls and next-session closing-price estimates for SPY, IEF and GLD; QQQ and IWM only in the measuring script (`scripts/contenders.py --universe`).
- Paper portfolios only: no real money, no accounts, no brokerage.
- Accuracy counts correct calls, not profit.
- The 2,871-call figures come from `scripts/contenders.py`; the app's own replay matches it call by call on a short replay and on the original 2023–2024 period. The full 2023–2026 run has not been compared with the app.

## Brand Commitments

- Name: MarketLens. Existing in-app line: "Keep the model honest."
- Voice: plain, exact, never hype; use the tool's own verdict wording ("no measurable difference"), never "the model lost".
- Visual reference supplied by the user for the promo page (binding as a direction to explore, style only): a light, lavender and white, card-based dashboard look with large numbers, small charts and a friendly hero illustration. Its template's name, logo and artwork must not be reused.

## Evidence on Hand

- Measured results: `scripts/contenders_output.txt`, `scripts/contenders_universe_output.txt`, `scripts/spike_replay_output.txt`.
- Real screen: `docs/model-history-contenders.png` (Model history after 26 replay sessions).
- 47 automated tests, two browser walkthroughs, 18 deliberate mutations all caught (`scripts/mutation_check.py`).
- Absent and never to be invented: users, testimonials, downloads, returns, profits, press.

## Product Principles

1. The measurement is the product; any model is just a contender.
2. Say the honest result first, even when it is "nothing wins".
3. A short record proves nothing; show the rule that refuses a verdict.
4. Every number traces to a committed file.

## Accessibility & Inclusion

No product-specific standard was set *(inferred)*: aim for WCAG 2.2 AA contrast and keyboard access; the page must read on a phone at 390 px.
