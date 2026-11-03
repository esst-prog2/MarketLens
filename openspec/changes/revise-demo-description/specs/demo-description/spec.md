## Purpose

Keep the README's demo description, which the final presentation follows, true to what the program actually shows on screen.

## ADDED Requirements

### Requirement: Demo description follows the program
README section 1 SHALL describe the final demonstration in three to six present-tense sentences that name real screens, controls and numbers. Every screen and control it names SHALL exist in the interface under that label, and the path SHALL run in Historical replay so that every screenshot can be reproduced offline.

#### Scenario: Names match the interface
- **WHEN** section 1 names a screen, data mode or button
- **THEN** the interface shows exactly that label

#### Scenario: Screenshots without the network
- **WHEN** the presenter follows section 1 with no internet connection
- **THEN** every step works and shows the same values as the description

### Requirement: Demo numbers are reproduced by a test
Every number in section 1 that the program computes SHALL be checked by an automated offline test that follows the same path: a Balanced $10,000 replay portfolio entered on 2023-01-03, then 26 trading sessions advanced. The test SHALL fail if the portfolio value, the count of scored and wrong five-session calls, the model and always-Up accuracy, either next-close error, or the shared-session count on the edge line differs from the text, as formatted on screen.

#### Scenario: Program changes, text does not
- **WHEN** a code or data change alters any of those values
- **THEN** the test fails until section 1 or the change is corrected

#### Scenario: Wrong calls are shown
- **WHEN** the path reaches Model history
- **THEN** the description states how many scored calls were wrong and how the model compares with the simple baselines, including when it does not beat them
