## Purpose

Keep the bundled offline replay recent while never rewriting the history that stored forecasts, tests and the demo were measured on.

## ADDED Requirements

### Requirement: Replay snapshot reaches a recent completed session
The bundled replay snapshot SHALL cover 2022-01-03 through the last completed exchange session before its recorded download, with no missing sessions and no filled prices. Its source file SHALL record the provider, URLs, retrieval time, coverage and SHA-256, and re-downloading with the recorded end date SHALL reproduce the same rows unless the provider revised them.

#### Scenario: Extended without rewriting
- **WHEN** the snapshot is extended to a later end date
- **THEN** every row of the previous snapshot is present with an identical date and closes

#### Scenario: Provider revision
- **WHEN** a re-download changes any earlier close
- **THEN** the downloader stops and reports which dates changed instead of writing the file

### Requirement: Existing replay databases survive a pure extension
When a replay database was created on an earlier snapshot, the application SHALL accept the current snapshot only if its first N rows reproduce the stored dataset hash for some N greater than the stored replay cursor, and SHALL then store the hash of the current snapshot. Any other dataset change SHALL still be refused with the existing instruction to use a new database path.

#### Scenario: Older, shorter snapshot
- **WHEN** the app starts with a database whose replay ran on the 2022–2024 snapshot
- **THEN** it starts, keeps every stored record, and its replay can continue past 2024-12-31

#### Scenario: Different data
- **WHEN** the stored hash matches no prefix of the current snapshot
- **THEN** the app refuses to start replay and names the new-database remedy
