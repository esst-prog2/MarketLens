## Purpose

Preserve the guided beginner learning experience while connecting transparent educational allocations to timestamped paper-investment results and a repeatable course demonstration.

## ADDED Requirements

### Requirement: Guided learning and educational selection
The system SHALL preserve the English goal/topic onboarding, separate experience and risk choices, time horizon, searchable nine-guide library, source links, saved guides and reading progress. It SHALL retain the three fixed educational allocations and explain their selection. Changing learning preferences SHALL NOT change existing holdings. No real payment SHALL be required.

#### Scenario: Returning learner
- **WHEN** a user revisits the application in the same browser
- **THEN** saved preferences and reading progress remain available, and an existing portfolio is not overwritten by a different suggested example

### Requirement: Timestamped paper portfolio
The system SHALL accept a virtual USD balance from $100 to $1,000,000 and invest fractional units using the selected existing allocation. In current-data mode it SHALL require valid, non-stale observations for all three assets and store entry prices and timestamps. During a closed market, latest available quotes from the most recently completed session SHALL be eligible and labelled as closed-market observations. Holdings SHALL remain fixed; newer quotes SHALL change value and profit/loss without executing additional trades. Accounting SHALL exclude fees, distributions and taxes, as disclosed.

#### Scenario: Price-only value change
- **WHEN** a $10,000 Balanced portfolio is created with all three entry prices at $100 and only SPY rises to $110
- **THEN** its value is $10,500 and its profit is $500, with unchanged units

#### Scenario: Missing or stale entry price
- **WHEN** any required current-data entry quote is missing, stale or from before the most recently completed session while the market is closed
- **THEN** new portfolio creation is rejected with an explanation and no partial investment is saved

### Requirement: State persistence and mode safety
Existing historical portfolios and heuristic forecast history SHALL survive migration, remain labelled as replay/legacy, and never be presented as current trained-model results. Current and replay portfolios SHALL persist independently across restarts. Resetting one mode SHALL NOT clear the other mode or browser learning progress. A partial refresh SHALL identify the individual valuation times and incomplete freshness instead of claiming an all-current portfolio value.

#### Scenario: Switch modes
- **WHEN** a user switches from current-data mode to replay and back
- **THEN** both portfolios retain their own units, dates and histories without using prices from the other mode

### Requirement: Repeatable class demonstration
The documented demonstration SHALL cover onboarding, learning, three current quote cards, both forecast horizons, a Balanced $10,000 allocation, changing paper P/L, visible forecast mistakes and errors, and automatic retraining/version comparison in labelled replay. It SHALL also show provider-failure behavior. The complete replay demonstration SHALL work offline after documented dependency installation and without paid credentials. Successful real intraday retrieval for all three symbols SHALL be verified separately; replay success alone SHALL NOT satisfy the current-data requirement.

#### Scenario: Presentation outside trading hours
- **WHEN** the presentation occurs while markets are closed
- **THEN** current mode shows the latest session timestamps and the presenter can use explicit replay for price changes, forecast evaluation and automatic retraining without misrepresenting historical data as live
