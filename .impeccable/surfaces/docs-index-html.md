---
version: 1
slug: "docs-index-html"
primary_target: "docs/index.html"
related_targets: ["promo-variants/a/index.html","promo-variants/b/index.html","promo-variants/c/index.html"]
---

# Design brief: MarketLens promo page

Impeccable `shape`, 2026-11-14. Target: `docs/index.html` (GitHub Pages). Content and order: `designs/promo-page.md` (approved). Mode: **Persuade**. Build path: code-led (no image generation on this machine).

Run unattended at the user's request ("csináld meg alaposan… később térek vissza"): interviews were answered from the approved design doc and the repository, and the decision round is a comparison page (`promo-variants/index.html`) instead of the live decision page. Assumptions are marked *(inferred)*.

## Job and audience
Classmates, the instructor and strangers open a link from the course; they give it a minute on a laptop or phone and score the program. Beginner investors are the people the lesson is for. *(inferred: most first visits are on a laptop in a lit room, during or after class.)*

## Outcome and proof
In one viewport a visitor learns what MarketLens measured, the verdict, and why they can trust it. Proof is the program's own output: the 2,871-call scoreboard, every call as a real data point, and the real Model history screen. The action is to look at the real thing: open the repository and run it.

## Selected directions (three built, the user picks one)

Seed: `seed:928a937ebefe0bc7` (persuade, direction scope). Grounded list, by resonance: 1 consumer test report, 2 sports league table, 3 sealed envelope / notary deposit, 4 weather-forecast verification sheet, 5 lab notebook with pre-registration, 6 school report card, 7 exchange LED ticker. The roll assigned candidate 3.

### A. Lavender scoreboard (user-pinned look)
- THESIS: the dashboard a beginner already trusts, holding a result no dashboard ever shows: no edge. Refuses the fintech hero that sells a prediction.
- OWN-WORLD: soft lavender ground, white cards with one shadow, a single violet ink for the model, warm gold for always up, slate for momentum; one rounded humanist display face, tabular figures everywhere.
- STORY: the visitor reads the verdict as a large number pair, sees the three rolling lines cross over four years, then the real screen, then the lesson.
- FIRST VIEWPORT: left, the verdict headline and one sentence; right, a large card with the three contenders' accuracies and the edge with its range; the GitHub action under the headline.
- FORM: user-pinned (`seed: none (pinned)`, "kinézete ilyen stílusú legyen": the supplied light lavender card dashboard). The hero illustration is replaced by the real app screenshot (craft floor: real illustration or none; no image generation here).
- FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

### B. Sealed envelope (assigned by the roll)
- THESIS: a forecast counts only if it was sealed before the outcome. The page is the deposit register: sealed, opened, scored. Refuses the chart-first finance page.
- OWN-WORLD: white envelope paper with the blue security-tint lattice from the inside of a bank envelope as the ground of sealed regions; violet date-stamp ink (the office stamp colour) for every date and verdict; a condensed grotesque for register headings, regular grotesque for text. State is a mark: a struck stamp for right, a cross for wrong, a perforation for pending.
- STORY: the visitor sees one forecast sealed on a date, opened five sessions later, then the register of all 2,871, then the verdict stamp, then the lesson.
- FIRST VIEWPORT: a large opened envelope across the page; inside, the scoreboard as a register slip; the verdict stamped across it in violet; the action as the register's signature line.
- FORM: candidate 3 of 7, `seed:928a937ebefe0bc7`.
- RAISES: from the provenance ribbon, known, inferred and pending states stay visibly distinct; from the cutting bench, state is a mark, not a hue; from the PC-98 field, one fixed grid that never shifts.
- FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

### C. Data field (challenger, competitive)
- THESIS: show all 2,871 calls, not a summary of them; a visitor sees with their own eyes that the model's field and always-up's field look the same. Refuses the explainer page.
- OWN-WORLD: pure black and white only, hairline bars, one monospace face for the numbers it actually prints; one full-frame inversion as the signature moment.
- STORY: three barcode fields, one per contender, each bar a real call; the visitor scans, the field inverts on the verdict line, then the lesson in plain type.
- FIRST VIEWPORT: the three barcode fields stacked full width with their accuracies at the right edge; the verdict line under them; the action at the bottom right of the frame.
- FORM: challenger `ikeda-datamatics` (wins product clarity, loses audience identification for beginners: competitive), fused with the product's facts.
- FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance.

Declined challengers (kept as raises above): provenance ribbon, sleeping city fold, cutting-bench select rail, itasha vinyl wrap, PC-98 sixteen-colour field. Not built but available: the consumer test report (my own top candidate, familiar), and the category standard (a plain fintech landing page).

## Scope and boundaries
One static page, fully interactive where its form needs it, at production fidelity; no change to the app. Anti-goals: invented users, returns or claims; "the model lost"; a fake app screen; a decorative chart.

## States and ranges
Data: 2,871 shared five-session calls per contender, 957 sessions of 20-session rolling accuracy (first point after 20 sessions), next-session MAE $2.27 vs $2.27. States: JavaScript off (all numbers present as text), data file missing (numbers still in text; charts hidden), reduced motion, 390 px phone.

## Constraints and open decisions
- Every number from `scripts/contenders_output.txt` or `docs/promo-data.js` (written by `scripts/export_promo_data.py`); counts labelled (five-session calls, next-session estimates, sessions).
- Nothing personal in `docs/`; variants live in `promo-variants/`, outside the published folder.
- Open for the user: which direction ships; whether to add the consumer-test-report variant; whether to enable GitHub Pages now.
