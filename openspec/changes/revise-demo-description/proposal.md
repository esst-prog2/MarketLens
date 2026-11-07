## Why

README section 1, *The demo*, was written in the first week, before the program existed. It now promises things the program no longer does: a "confidence score" (replaced by the measured hit rate after the HW4 spike), a "suggested model allocation" (the weights are fixed, and the button has said **Apply fixed allocation** since HW6), and a model that learns from its errors to get better (since 2026-10-11 MarketLens is a tool that measures whether a model beats simple baselines, and the measured answer is no). The demo on 1 December 2026 also changes format: five minutes of screenshots instead of three minutes of live use, scored by the audience on the program, not on the slides. This is the last point at which the description can change.

## What Changes

- Rewrite README section 1 only, keeping the first-week path: a beginner picks the Balanced profile with $10,000, applies the allocation, watches the paper portfolio move, then opens Model history and sees earlier calls, including the wrong ones, scored against what actually happened.
- Show the path in **Historical replay — offline**, so every screenshot can be reproduced exactly and does not depend on market hours or on Yahoo being reachable on the day the screenshots are taken.
- Use the program's real numbers after 26 presses of **Next trading day** from 2023-01-03: portfolio $10,394.82; 66 scored five-session calls, 27 of them wrong; model accuracy 59.1%, equal to always-Up; next-close error $1.89 against $1.85 for repeating the last close.
- Add a test that replays those 26 sessions and fails if any number written in section 1 stops matching the program.
- Leave sections 2–5 (the original brief) and the application unchanged.

Old text (first week), kept here for the record:

> I open MarketLens in the browser as a beginner investor with little knowledge of financial markets and select the Balanced profile with a virtual starting balance of $10,000. The dashboard shows current market views for US Equities, US Government Bonds, and Gold, each with a forecast direction, confidence score, risk level, and a short explanation written for non-expert users. I apply the suggested model allocation to the virtual portfolio, which is then tracked using real market prices and shows how much the simulated investment gains or loses over time. I open Model History and compare earlier forecasts with actual market outcomes, including incorrect predictions. The system stores these forecast errors and uses them during periodic model retraining so that later model versions can be evaluated against earlier ones.

Proposed text (first draft; the final text, revised on 2026-11-03 after `contender-leaderboard` put the contenders table on Model history, is README section 1):

> I open MarketLens at http://127.0.0.1:8080 as a beginner investor, set Data mode to **Historical replay — offline**, and on the **Practice** screen choose the Balanced profile with a virtual starting balance of $10,000. Market outlook shows SPY (US equities), IEF (US Treasury bonds) and GLD (Gold), each with a five-trading-session Up/Down call headed by the measured hit rate of earlier calls, a next-session closing-price estimate and a risk level. I press **Apply fixed allocation**, which buys $5,000 of SPY, $3,500 of IEF and $1,500 of GLD at the 2023-01-03 closes, and after 26 presses of **Next trading day** the portfolio is worth $10,394.82. On **Model history** every call stays on record: 27 of the 66 scored five-session calls are wrong, the model's 59.1% accuracy is exactly what always guessing Up gets, and its $1.89 next-close error is worse than the $1.85 of simply repeating the last close. The model retrains automatically after every session, and the first complete frozen-version comparison scores an older and a newer version on the same 20 sessions, so the screen shows whether the newer one is actually better.

## Capabilities

### New Capabilities
- `demo-description`: README section 1 describes the final demonstration as the program actually behaves, with numbers that a test reproduces from the replay.

### Modified Capabilities
None. The MVP change (`marketlens-course-mvp`) was never archived, so there are no main specs; its *Repeatable class demonstration* requirement still describes the longer class walkthrough in README *Class demonstration* and is not changed.

## Impact

- `README.md` section 1 only.
- New `tests/test_demo_description.py` (offline, about 30 s).
- No change to application code, data, APIs or dependencies.
