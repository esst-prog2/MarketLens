## Context

The final demo on 1 December 2026 is five minutes of screenshots, not a live run; the audience scores the program. The first-week path stays (Balanced $10,000 → portfolio → Model history), but the README wording must match the program as it is after HW4–HW6 and the contender work.

## Goals / Non-Goals

**Goals:** a section 1 that is true, concrete and short; numbers that cannot silently drift from the program.

**Non-Goals:** changing the app, the original brief (sections 2–5), the longer *Class demonstration* walkthrough, or producing the slides themselves.

## Decisions

- **Historical replay, not Current market data.** Replay is deterministic and offline: the screenshots can be retaken any day with identical values. Current data changes daily, shows "closed" outside exchange hours, and depends on Yahoo. Current mode still exists and stays in the *Class demonstration* section.
- **26 sessions.** It is the shortest replay that matures price and direction errors and completes one 20-session frozen-version comparison (already the README class-demo number).
- **State the unflattering result.** At 26 sessions the model equals always-Up (59.1%) and loses to last-close on price ($1.89 vs $1.85). Since the project measures models rather than selling one, the demo says so.
- **Numbers as the screen formats them.** Money with two decimals (`Intl` en-US), percentages with one decimal, matching `web/app.js` `money` and `percent`, so a screenshot and the text agree character for character.
- **A test pins the numbers** by replaying the path through `MVPService`, the same service the screens read.

## Risks / Trade-offs

- [Replay is 2023 data, not today's market] → the description and screen say "Historical replay — offline"; nothing is presented as live.
- [26 sessions is a small sample] → the full 1,491-call comparison (README *Contenders side by side*) backs it up; the presentation can cite both.
