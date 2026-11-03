## Context

`training_prices.csv` (753 sessions, 2022-01-03..2024-12-31) holds Yahoo daily closes, not dividend-adjusted, for SPY, IEF and GLD. The symbols are fixed through `core.ASSETS`, which `load_prices`, `validate_history`, `features`, `fit_model`, `predict` and the baselines all read. Replay state stores `data_hash(prices)` and refuses any change. The demo text and `tests/test_demo_description.py` depend on the first 278 sessions.

## Goals / Non-Goals

**Goals:** recent replay data with unchanged history; existing databases keep working; contenders measured on five instruments; app behaviour unchanged.

**Non-Goals:** new cards, profiles or a five-instrument app model (after 9 November); earlier history before 2022 (it would move the practice start and the demo numbers); dividend-adjusted returns.

## Decisions

- **Fixed end date.** The downloader takes `period2` = 2026-11-03 00:00 UTC and keeps only completed sessions. It compares the result with the existing file and stops if an earlier close changed. *Alternative:* "until now". Rejected because it is not reproducible.
- **Prefix acceptance.** On a hash mismatch, try `data_hash(prices[:n])` for n from cursor+1 to len(prices); on a match, update `m_state.dataset`. That is at most about 460 hashes, once at startup. It is safe because training, issuance and evaluation for every stored record used only rows up to the cursor, and a matching prefix proves those rows are identical. *Alternative:* store the row count from now on. Rejected because it does not help existing databases.
- **Symbols as a parameter with the old default.** `features(rows, i, s, symbols=ASSETS)` keeps the one-hot over the given list. `fit_model(rows, symbols=None)` records `symbols` in metadata only when it is not the default, so default model versions and their IDs are unchanged. `predict` reads the list from metadata. Baselines and `require_contiguous` take the same optional list.
- **Separate universe file.** `universe_prices.csv` (date, SPY, IEF, GLD, QQQ, IWM) keeps the app's loader and replay hash independent of the experiment. A test checks that its three shared columns equal the replay snapshot.

## Risks / Trade-offs

- [A Yahoo revision later breaks the prefix guarantee] → the downloader refuses to write; the committed file stays the source of truth.
- [Harness run time doubles, and the universe run adds 5/3 more examples per fit] → it is run once, with the output committed; tests use short replays.
- [QQQ and SPY are highly correlated] → stated in the output note; it widens style coverage, not independence.
