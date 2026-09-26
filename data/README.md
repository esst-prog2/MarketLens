# Historical sample

`prices.csv` contains 252 actual daily closing prices from 2024 for SPY, IEF,
and GLD, downloaded from Yahoo Finance. See `sources.json` for the exact URLs,
retrieval timestamp, coverage and price convention. The app works offline
using this committed sample. These are historical prices, never live quotes.

The instruments are proxies for the three markets in the project brief:

- [SPY](https://www.ssga.com/us/en/individual/etfs/state-street-spdr-sp-500-etf-trust-spy): US large-cap equities.
- [IEF](https://www.ishares.com/us/products/239456/ishares-7-10-year-treasury-bond-etf): US Treasury bonds with 7–10 year maturities.
- [GLD](https://www.ssga.com/us/en/individual/etfs/spdr-gold-shares-gld): gold exposure.

Prices are USD daily closes, not dividend-adjusted total returns. The demo
does not include distributions, taxes, fees or slippage. The Yahoo chart
endpoint is an unofficial integration and may change or become unavailable;
the bundled snapshot avoids a runtime dependency on that service.

To download the same period again: `python scripts/download_sample.py`.
This needs internet access and replaces the sample files. Provider revisions
may change historical data; use a new `--database` path if the dataset changes.
The loader rejects missing, duplicate, unsorted, non-finite and non-positive
values rather than filling gaps with invented prices. The downloader keeps
only trading dates available for all three instruments.

## Trained MVP replay

`training_prices.csv` is a separate 753-session snapshot, 2022-01-03 through
2024-12-31. `training_sources.json` records the Yahoo URLs, download timestamp,
price convention and SHA-256. `python scripts/download_training_sample.py`
re-downloads this file after dependency installation; history revisions require a
new experiment database. Exchange-calendar validation rejects gaps, never fills
missing prices. The original 2024 sample remains unchanged for legacy inspection.

Current mode retrieves observations independently; it never treats bundled replay
prices as current. Both snapshots use USD closes, excluding distributions and costs.
The unofficial source has no availability guarantee or granted redistribution
license. This repository records a course experiment, not a commercial feed.
