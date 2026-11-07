## 1. Scoring

- [x] 1.1 Add `edge(calls, model, baselines)` to `marketlens/contenders.py`: block-paired difference and approximate 95% range for direction and next-close error, verdict, 30-session minimum; hand-counted test written first
- [x] 1.2 Add `rolling(calls, window=20)` with a hand-counted test
- [x] 1.3 Print the edge lines in `scripts/contenders.py` and refresh `scripts/contenders_output.txt`

## 2. Stored contenders

- [x] 2.1 Issue and store baseline records in `MVPService._issue` under the no-backfill rule; test that they are stored with the model's and never backfilled in current mode
- [x] 2.2 Add `contenders` (board, edge, rolling) to the snapshot; test that it equals `leaderboard(replay(...))` on a short replay
- [x] 2.3 Measure seconds per replay step before and after

## 3. Model history screen

- [x] 3.1 Leaderboard table, edge lines and rolling chart in `web/mvp.js` / `web/index.html` / `web/style.css`, with escaped names and the 390 px layout
- [x] 3.2 Extend `tests/browser_mvp.py` to check the table and chart after 26 sessions

## 4. Deliver

- [x] 4.1 README: contenders section and Model history description; PLANNING_LOG entries
- [x] 4.2 Full test suite and both browser workflows green; `openspec validate contender-leaderboard --strict`; commit and push
