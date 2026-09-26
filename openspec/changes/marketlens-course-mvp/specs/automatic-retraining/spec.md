## Purpose

Automatically incorporate newly known market outcomes into reproducible model versions while preventing future-information leakage and making failures and model comparisons visible.

## ADDED Requirements

### Requirement: Automatic training trigger
While the local server runs, the system SHALL check for retraining after each newly ingested complete daily session for all three instruments and on startup. It SHALL automatically train when sufficient new eligible data exists, at most once successfully per completed-data cutoff. Startup SHALL catch up to the latest eligible cutoff without replaying every missed live job. It SHALL state that scheduled work does not run while the application or computer is off.

#### Scenario: New completed session
- **WHEN** a valid new shared daily close is ingested and eligible labelled training examples increase
- **THEN** a retraining run begins automatically without a button press or application restart

#### Scenario: Repeated refresh or restart
- **WHEN** the same cutoff has already been processed successfully
- **THEN** another refresh or restart does not create a duplicate successful model version

### Requirement: Chronological training and evaluation
All features, preprocessing, fitted parameters and probability calibration SHALL use only information available at their recorded cutoff. Training SHALL exclude examples whose target outcomes are not yet known. Evaluation predictions SHALL use versions fitted and calibrated before the evaluation period, with forecast horizons excluded across split boundaries. Retraining SHALL include eligible correct and incorrect examples rather than learning only from errors.

#### Scenario: Five-session label not yet known
- **WHEN** an observation's five-session target lies after the current data cutoff
- **THEN** that example is excluded from directional training even if its one-session outcome is already known

#### Scenario: Future data isolation
- **WHEN** later observations beyond a simulated cutoff are changed
- **THEN** the model version and predictions issued at that cutoff remain unchanged

### Requirement: Versioned runs and failure recovery
The system SHALL retain each run's status, trigger cutoff, training/calibration ranges, data identity, model configuration, version and errors. A successful run SHALL publish a complete usable version atomically. Failed, overlapping or insufficient-data runs SHALL NOT discard the last usable version. The UI SHALL show the latest successful training cutoff and last run status.

#### Scenario: Failed scheduled run
- **WHEN** retraining fails or validation detects unusable data
- **THEN** the previous usable model remains active, the failure is visible and a bounded later retry is possible

### Requirement: Comparable versions
The system SHALL compare consecutive successful versions on the same later observations excluded from both versions' fitting and calibration. Before enough shared outcomes exist it SHALL display pending comparison. It SHALL report improvements and regressions without claiming retraining guarantees improvement.

#### Scenario: Shared future observations mature
- **WHEN** both frozen versions have recorded evaluation predictions for a later session and the target outcome becomes available
- **THEN** their comparison uses those same observations and shows version identifiers, period and sample counts

### Requirement: Demonstrable automatic retraining in replay
Replay SHALL use the same eligibility and training rules against its simulated clock, with distinct replay model records. The bundled demo SHALL include enough earlier history to demonstrate an automatic retraining event and at least one version comparison without accessing future observations during training.

#### Scenario: Class presentation advances the clock
- **WHEN** replay advances past a newly eligible completed session
- **THEN** retraining occurs automatically and subsequent replay sessions expose forecast outcomes and model comparisons without waiting real days
