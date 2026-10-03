## Purpose

Make two distinct forecast targets understandable and measurable, keeping genuine probability estimates separate from heuristic strength and comparing forecasts with later observed results.

## ADDED Requirements

### Requirement: Five-session directional probability
For each supported instrument with sufficient valid history and a usable trained model, the system SHALL issue an Up or Down forecast for the fifth trading-session close relative to the latest completed closing price. As its headline it SHALL display the measured hit rate of earlier evaluated five-session calls whose stated confidence fell in the same 0.2-wide band, with the count, only when at least 30 such calls exist; otherwise it SHALL state that there is not enough history yet. The model's own estimate SHALL appear only as secondary text labelled uncalibrated. It SHALL also display the reference close/date, target session and model version. A heuristic trend score SHALL NOT be relabelled as a probability. (HW4 spike, 2026-10-03: a full replay delivered 52/52/55% in bands that promised 55/67/85%.)

#### Scenario: Measured hit rate interpretation
- **WHEN** the selected direction is Up with a model estimate of 0.65 and 310 earlier evaluated calls in the 0.6-0.8 band were right 52% of the time
- **THEN** the UI shows Up with 52% of 310 earlier calls right as the headline, and 65% only as an uncalibrated model estimate, not as a probability, return or guarantee

#### Scenario: Not enough evaluated history
- **WHEN** fewer than 30 earlier evaluated calls fall in the forecast's confidence band
- **THEN** the UI states that there is not enough history yet instead of showing a hit rate

#### Scenario: Model unavailable
- **WHEN** training history is insufficient or no usable model exists
- **THEN** the UI states why a probability is unavailable rather than inventing a percentage

### Requirement: Separate next-session closing-price estimate
The system SHALL additionally display a finite positive USD estimate for the next trading-session close, with its own target session, reference date and model version. It SHALL NOT attach the five-session directional probability to this price target. Forecasts SHALL use only completed daily observations available at issuance; intraday quote changes SHALL NOT silently rewrite them.

#### Scenario: Weekend or holiday horizon
- **WHEN** a forecast is based on Friday's close and Monday is an exchange holiday
- **THEN** the price target is Tuesday's closing session, not Saturday or Monday

#### Scenario: Intraday display
- **WHEN** the current price updates while the latest completed close is unchanged
- **THEN** the quote changes independently and the forecast retains its explicitly displayed daily reference date and target

### Requirement: Forecasts precede outcomes and remain auditable
The system SHALL persist both forecasts, probabilities, input cutoff, issuance time, reference prices, target sessions, data mode and model version before their outcomes become available. Each horizon SHALL remain pending until its completed target-session close exists. Refreshes and retraining SHALL NOT replace previously issued predictions. Duplicate daily issuance for the same instrument, mode and horizon SHALL be prevented.

#### Scenario: New model version
- **WHEN** automatic retraining produces another model
- **THEN** earlier forecasts retain their original values and model associations while subsequent session forecasts can use the new version

### Requirement: Directional and price-error evaluation
The system SHALL compare the five-session close with the reference close: a strict increase is Up, a strict decrease is Down, and equality is Flat. A Flat outcome SHALL count as incorrect for an Up or Down prediction and remain visible in outcomes. For next-session price forecasts it SHALL report absolute dollar error and absolute percentage error using the actual target close as denominator. Summaries SHALL include evaluated counts, pending counts, directional accuracy, MAE and mean absolute percentage error for their respective horizons, excluding pending records.

#### Scenario: Price error arithmetic
- **WHEN** the predicted close is $100 and the actual target close is $102
- **THEN** the error is $2 and approximately 1.9608%, with full precision retained for aggregation

#### Scenario: Wrong and flat predictions
- **WHEN** the model predicts Up and the five-session close is unchanged or lower
- **THEN** the record is marked incorrect and included in accuracy rather than hidden

### Requirement: Probability reliability and baseline comparisons
The system SHALL present probability estimates as experimental and evaluate them using outcomes not used to fit or calibrate the corresponding model. It SHALL report a Brier score for selected-direction correctness and confidence-bin observed correctness rates with sample counts. It SHALL compare five-session directional accuracy with always-Up and the existing momentum rule, and next-session MAE with a last-close forecast on identical eligible records. Replay and current-data results SHALL be separated; overlapping forecast windows SHALL be identified as non-independent.

#### Scenario: No completed probability outcomes
- **WHEN** all stored probability forecasts are pending
- **THEN** reliability metrics show insufficient outcomes, not zero error or perfect calibration

#### Scenario: Honest benchmark
- **WHEN** a baseline performs better than the trained model
- **THEN** the comparison displays that result without replacing or omitting the model's mistakes
