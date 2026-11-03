## 1. Test first

- [ ] 1.1 Add `tests/test_demo_description.py`: replay a Balanced $10,000 portfolio from 2023-01-03 for 26 sessions and assert, as formatted on screen, $10,394.82, 66 scored and 27 wrong five-session calls, 59.1% model and always-Up accuracy, $1.89 and $1.85 next-close errors and one complete version comparison; also assert each of those strings appears in README section 1
- [ ] 1.2 Run it against the old section 1 and record that it fails

## 2. Description

- [ ] 2.1 Replace README section 1 with the approved text from proposal.md
- [ ] 2.2 Check every named label (Historical replay — offline, Practice, Market outlook, Apply fixed allocation, Next trading day, Model history) against `web/index.html`
- [ ] 2.3 Run the new test and the full suite green

## 3. Deliver

- [ ] 3.1 Append the decisions to PLANNING_LOG.md
- [ ] 3.2 Validate with `openspec validate revise-demo-description --strict`, commit and push
