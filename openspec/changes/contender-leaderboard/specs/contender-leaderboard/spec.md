## Purpose

Show on screen, not only in a script, whether the trained model beats simple baselines, measured on the same observations, with its uncertainty and over time.

## ADDED Requirements

### Requirement: Contender forecasts are stored records
Whenever the model issues forecasts, the system SHALL also issue and store the forecasts of always-up, 20-session momentum and last-close for the same reference session, using only sessions up to that reference session. Stored contender forecasts SHALL be immutable and SHALL follow the same no-backfill rule as the model: in current mode no contender forecast is issued for an outcome that is already observable.

#### Scenario: Issued together
- **WHEN** the model issues forecasts for a reference session
- **THEN** each baseline has a stored forecast for that session, symbol and horizon it answers

#### Scenario: No live backfill
- **WHEN** current mode catches up with history whose outcomes are already known
- **THEN** no contender forecast is stored for those outcomes

### Requirement: Leaderboard on shared observations
Model history SHALL show one row per contender with five-session calls, accuracy, Brier error (only for contenders that state a confidence), next-close estimates and MAE. Each horizon SHALL be scored only on the observations that every contender answering that horizon has evaluated. A contender that does not answer a horizon SHALL show a dash for it.

#### Scenario: Same numbers as the script
- **WHEN** replay has been advanced over the full snapshot
- **THEN** the leaderboard values equal those printed by `scripts/contenders.py`

#### Scenario: Contender missing an observation
- **WHEN** one contender has no forecast for a reference session
- **THEN** that session is left out for every contender on that horizon

### Requirement: Edge over the best baseline with uncertainty
The system SHALL show the model's direction accuracy minus the best baseline's direction accuracy, and the model's next-close MAE minus last-close MAE, each with an approximate 95% range. Both SHALL be computed on the shared observations. The range SHALL be computed from blocks of five consecutive reference sessions, so that overlapping five-session targets are not treated as independent. The verdict SHALL be "better" or "worse" only when the range excludes zero, and "no measurable difference" otherwise. With fewer than 30 shared reference sessions it SHALL state that there is not enough history yet, and show the count.

#### Scenario: Difference within noise
- **WHEN** the range includes zero
- **THEN** the verdict is "no measurable difference", whichever accuracy is higher

#### Scenario: Short history
- **WHEN** fewer than 30 shared reference sessions have matured
- **THEN** the edge shows "not enough history yet" and the current count out of 30

### Requirement: Rolling accuracy over time
Model history SHALL show a chart with one line per direction contender: the accuracy of its matured shared five-session calls over the latest 20 reference sessions, plotted by reference date, labelled with each contender's name. It SHALL appear only once 20 shared reference sessions have matured.

#### Scenario: Lines cross
- **WHEN** a baseline is ahead in one period and the model in another
- **THEN** the chart shows both periods, and the leaderboard still reports the whole-period figures
