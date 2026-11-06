# Participant experiment: analysis plan (side study, T070)

Draft by ayush-main for Ayush to check. Written **before any data come in**; changes after data arrive must be listed under "Deviations" with a date.

## Design
- Online, between-subjects. Each participant sees **one** of 18 videos: 3 pitches x founder gender (male / female) x founder age (22 / 28 / 35). Assignment is uniform random per session (experiment/app.py) and passed to the form as URL parameters `video`, `pitch`, `gender`, `age`, `consent`.
- Within each pitch, the 6 videos must have the same script, length and delivery, so that only gender and age differ. TODO (Ayush): describe how the videos were made (actors, voice, AI-generated?) and how the scripts were kept identical.
- Consent screen before the video (18+, voluntary, anonymous). No names, emails or IDs collected.

## Outcomes
TODO (Ayush): list the exact form questions. Suggested, in order of priority:
1. **Primary: investment allocation**, e.g. "Out of ₹1,000 (hypothetical), how much would you invest in this business?" (0-1000).
2. Secondary: likelihood to invest (1-7), perceived competence (1-7), perceived growth potential (1-7), perceived risk (1-7).
3. Manipulation checks: "What was the founder's gender?" and "Roughly how old was the founder?" (Planned exclusion: wrong gender answer.)
4. Attention check: one instructed item.
5. Participant background (optional, coarse): own gender, age band, any investing experience.

## Planned models
- Primary: `allocation ~ female + C(age) + C(pitch)` (OLS, robust SEs). Effect of interest: coefficient on `female`.
- Moderation (H4 analogue): `allocation ~ female * C(age) + C(pitch)`; report the interaction as exploratory unless n is large (see below).
- Secondary outcomes: same model per outcome; Holm correction across secondary outcomes.
- Participant-gender moderation (H5 analogue, exploratory): add `female * participant_female`.
- Language: associations within a randomised design can be described as effects of the assigned video, but keep claims to this sample (students / online convenience sample).

## Exclusions (fixed now)
1. Did not consent (no data recorded anyway).
2. Failed the attention check.
3. Wrong answer to the founder-gender manipulation check.
4. Duplicate submissions (same form session) beyond the first.
Report results with and without exclusions 2-3.

## Minimum responses and the report decision
Power for the gender main effect (two groups, alpha 0.05, power 0.80; statsmodels TTestIndPower):
- medium effect d = 0.5: 64 per gender group, about 128 usable responses in total;
- small-to-medium d = 0.3: 175 per group, about 350 in total.

Proposal: include the experiment in the report as a short section if there are at least 128 usable responses; below that, report it as a pilot in an appendix (descriptives only, no inference on the interaction). Gender x age interaction tests need far more and stay exploratory either way. TODO (Ayush + Abhiraj): confirm this threshold and the data-collection end date.

## Ethics and data handling
- TODO (Ayush): ask the course instructor / IIIT whether an online anonymous study needs ethics approval; record the answer and date in board/tasks/T070_participant_experiment.md.
- Raw responses stay out of git (export to a private folder). Only aggregated, anonymous tables may be committed.

## Deviations
(none yet)
