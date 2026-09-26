## Purpose

Provide sourced observations for three real market instruments, with clear freshness and failure states and a separate reproducible historical demonstration mode.

## ADDED Requirements

### Requirement: Free intraday market observations
The system SHALL obtain actual intraday USD observations and daily closing prices for SPY, IEF and GLD without requiring a paid subscription. While the local application runs, it SHALL attempt an initial refresh and subsequent refreshes every five minutes during regular trading sessions. Polling frequency SHALL NOT be presented as guaranteed provider latency.

#### Scenario: Successful current-data refresh
- **WHEN** the provider returns valid newer observations for the supported instruments
- **THEN** the current-data view updates their prices and shows each observation's timestamp, source and retrieval time
- **AND** it identifies delayed or unknown-delay data without claiming exchange-level real-time coverage

#### Scenario: Free access unavailable
- **WHEN** the provider rejects a request, rate-limits access or requires payment
- **THEN** the application reports the failure, retains usable cached observations with their original times, and never purchases access or substitutes invented prices

### Requirement: Explicit freshness and session state
The system SHALL distinguish current-session observations, stale observations, closed-market prices and unavailable data using the instruments' exchange calendar. During an open session, a quote older than 30 minutes SHALL be marked stale. A successful fetch of an unchanged old quote SHALL NOT make it fresh. The 30-minute threshold is a display rule, not a promised maximum provider delay.

#### Scenario: Market closed
- **WHEN** the application opens on a weekend, exchange holiday or after the regular session
- **THEN** it identifies the closed market and displays the last observation time without presenting a fabricated price change

#### Scenario: Missing observation
- **WHEN** one instrument has no usable observation
- **THEN** the affected card states that data is unavailable while the other instruments remain inspectable

### Requirement: Validated daily history
The system SHALL validate symbol, currency, timestamps, chronological uniqueness, finite positive prices and completed-session status before using history for forecasting or training. Missing expected sessions SHALL prevent affected forecast/training windows from being treated as consecutive trading sessions. It SHALL expose a useful reason for rejected or insufficient data.

#### Scenario: Incomplete session or missing daily bar
- **WHEN** today's daily bar is still provisional or an expected completed session is absent
- **THEN** it is excluded from completed-history processing and the system does not silently compress the forecast horizon or manufacture a closing price

### Requirement: Current and replay modes are isolated
The system SHALL retain an explicitly labelled historical replay using sourced bundled observations. Current quotes, portfolios, forecast histories and training runs SHALL remain isolated from replay state. A network failure SHALL NOT silently switch the user's current-data portfolio to historical prices.

#### Scenario: Offline class demonstration
- **WHEN** the user explicitly selects replay without internet access
- **THEN** the application displays the simulated date, advances through bundled sessions, and never describes replay observations as today's quotes
