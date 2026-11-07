# Participant experiment: analysis plan (side study, T070)

Written **before any data come in**; changes after data arrive go under "Deviations" with a date.

## Design
- Online. Each participant sees **three** pitch videos, one for each business (A, B, C), and is assigned at random to one of 6 groups: 3 orders x founder voice (F or M, the same for all three pitches).
- The orders form a Latin square: across O1-O3 each business appears once at each stated founder age (22, 28, 35). So founder age varies **within** participants and voice **between** participants.

| Order | Pitch 1 | Pitch 2 | Pitch 3 |
| --- | --- | --- | --- |
| O1 | A, 22 | B, 28 | C, 35 |
| O2 | B, 35 | C, 22 | A, 28 |
| O3 | C, 28 | A, 35 | B, 22 |

- Within a business, the six videos share one script; only voice and stated age differ. Video lengths differ somewhat (e.g. 53-80 s for the recorded ones), so `watch_seconds` and video length are recorded.
- Consent screen first (18+, voluntary, anonymous). No incentive or bonus draw; the end screen shows the study contact for questions.

## Measures (all taps, about 45 s per pitch)
After each pitch, on one screen, in this order (items 1-3):
1. **Primary: investment decision**, "Would you invest in this business?": Yes / Yes, but at a lower valuation than the founder asked for / No (`invest_decision` = yes / yes_lower / no; options always in this order). The founders' asks are in lakhs, so a rupee amount out of ₹1,000 did not fit. Outcomes: `invest_any` = yes or yes_lower (0/1); among those, `wants_lower_valuation` = yes_lower (0/1), the side-study analogue of the main study's valuation haircut.
2. **Conjunction fallacy** (lecture "Conjunction Fallacy"), 2 items asked after **every** pitch about that pitch ("Think about this business / this founder"), each with three options, order shuffled per participant and pitch: a single event, that event plus another, and the opposite event. Business: still running in 3 years / still running and expanded to another state / no longer running. Founder: steps back within 5 years / steps back to focus on family / still running the business. Choosing the conjunction = fallacy; the third option gives a non-fallacy alternative to the single event. Fallacy rate = share choosing the conjunction among all answers (and, as a check, among those not choosing the opposite event). The founder item carries a gender stereotype, so its fallacy rate may differ by founder voice. Each participant answers each item three times (once per pitch), so founder age can also be compared within participants; repeated answers may drift with practice, so pitch position is controlled.
3. **Question focus (optional)**: "Optional: which question would you most want to ask this founder?", 4 options per business (2 promotion, 2 prevention, following the project codebook), shown in random order. Outcome: picked a prevention question (0/1), among pitches where a question was picked; a blank answer is saved as `question_focus = skipped`.
4. Attention / manipulation check (once, at the end): "The founders' voices were all female / all male / some of each / not sure".
5. Participant (once, at the end): age band, gender, ever invested (yes/no).

## Planned models
Data: one row per participant x pitch (3 rows each). Standard errors clustered by participant.
- Investment (primary): logit `invest_any ~ female_voice * C(founder_age) + C(business) + C(position)`; report average marginal effects. Main term: `female_voice`.
- Investment (secondary): same right-hand side, logit on `wants_lower_valuation` among yes answers; robustness: ordered logit on no < yes_lower < yes.
- Question focus: same right-hand side, logit on `picked_prevention` among pitches where a question was picked; report average marginal effects. This links the side study to the main study's H1 (more prevention questions for female founders). Because the item is optional, also report the skip rate by `female_voice` (a difference would mean selection into answering).
- Exploratory: `female_voice x participant_gender`; `female_voice x invested_before`.
- Exploratory (lecture items): fallacy per item and pitch, logit on `female_voice * C(founder_age) + C(business) + C(position)` (key test: founder item, female vs male voice).
- Associations from a randomised assignment may be described as differences between assigned conditions, limited to this convenience sample.

## Exclusions (fixed now)
1. Voice check answered wrong ("all male" for a female-voice group or the reverse). "Not sure" is kept.
2. Any pitch with `watch_seconds` below 90% of the video length is impossible by design (the app blocks it), so no time-based exclusion.
3. Duplicate participant ids beyond the first submission.
Report results with and without exclusion 1.

## Minimum responses and the report decision
Voice is between participants. Power for the voice main effect (two groups, alpha 0.05, power 0.80; statsmodels TTestIndPower, treating each participant's share of "would invest" answers across the three pitches as one observation):
- medium effect d = 0.5: 64 participants per voice, about 128 in total;
- small-to-medium d = 0.3: 175 per voice, about 350 in total.
Proposal: a short report section if there are at least 128 usable participants; below that, an appendix pilot (descriptives only). Age effects (within participants) and interactions stay exploratory. TODO (Ayush + Abhiraj): confirm the threshold and the end date.

## Ethics and data handling
- TODO (Ayush): ask the course instructor / IIIT whether this online anonymous study needs ethics approval; record the answer in board/tasks/T070_participant_experiment.md.
- Raw responses stay in the Google Sheet and out of git. Only aggregated, anonymous tables may be committed.

## Deviations
- 2026-11-07: design changed from "1 of 18 videos per participant" to the 6-group, 3-pitch design above (Ayush). Typed questions, timed/untimed groups, BIS/BAS scale and open-text items dropped to keep each pitch under a minute.
- 2026-11-07: added 2 closing conjunction-fallacy items, before data collection (Ayush); 2 bias blind spot items were added and then removed the same day, before any data.
- 2026-11-07: a third option (the opposite event) added to each conjunction item, before any data (Ayush).
- 2026-11-07: optional bonus draw removed before any data (no prize budget; Ayush). The end screen now shows the study contact for questions.
- 2026-11-07: before any data (Abhiraj): (a) the ₹0-1,000 investment item replaced by a 3-option decision (yes / yes at a lower valuation / no), because the founders' asks are in lakhs; (b) the 2 conjunction items moved from the end to after every pitch, worded about that pitch; (c) the question pick made optional. Sheet columns change: `invest_rupees` and `cf_last_business` removed; `invest_decision` added; `cf_*` columns now vary per pitch row. The Sheet's `responses` tab must be cleared before launch so the header row matches.
