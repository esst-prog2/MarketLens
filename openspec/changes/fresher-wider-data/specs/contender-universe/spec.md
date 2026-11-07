## Purpose

Measure contenders on more instruments than the app currently shows, so the evidence about whether a model beats the baselines is not limited to three ETFs.

## ADDED Requirements

### Requirement: Contenders on a chosen instrument list
The measuring harness SHALL run every contender on a given list of instruments from a sourced, validated snapshot that has all of them on every session. The default list SHALL remain SPY, IEF and GLD, and the application's screens, portfolios and model versions SHALL be unaffected by the wider list.

#### Scenario: Five instruments
- **WHEN** `scripts/contenders.py --universe` runs on SPY, IEF, GLD, QQQ and IWM
- **THEN** each contender's calls cover all five instruments on the same shared observations, and the leaderboard and edge lines are printed as for three

#### Scenario: Default unchanged
- **WHEN** the harness or the app runs without an instrument list
- **THEN** the results equal those of SPY, IEF and GLD before this change

### Requirement: Universe snapshot is sourced like the replay snapshot
The wider snapshot SHALL cover the same sessions as the replay snapshot, record its sources and SHA-256, and contain the same SPY, IEF and GLD closes as the replay snapshot.

#### Scenario: Same three closes
- **WHEN** both snapshots are loaded
- **THEN** their SPY, IEF and GLD columns are identical on every session
