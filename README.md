streamlit website for our project, looking at the code is akin to cheating :]

## Design
Side study T070 (CLAUDE.md, "Side study"). One Streamlit app runs the whole flow:
consent -> 3 x (pitch video -> invest + optional question pick -> 2 conjunction items on their own screen) -> 4 short closing questions (voice check, ever invested, age group, gender) -> save -> debrief with the contact for questions.

- 6 groups = 3 orders (O1-O3) x founder voice (F or M, the same for all three pitches), assigned at random.
- Each order shows businesses A, B and C once; across the orders every business appears once at each age (22, 28, 35).
- Per pitch, screen 1: would you invest? (Yes / Yes, but at a lower valuation than asked / No; the founders' asks are in lakhs, so no rupee amount) and, optionally, the question you would most want to ask (2 promotion and 2 prevention options, shuffled; `question_focus = skipped` if left blank).
- Per pitch, screen 2: the 2 conjunction-fallacy items about that business and founder (options shuffled). They come after the question pick so the founder item ("steps back ... to focus on family") cannot prime it.
- End: age group (Under 18 / 18-24 / 25-34 / 35-44 / 45-54 / 55 or older / Prefer not to say) and gender (Woman / Man / Non-binary / Prefer to self-describe, with optional short text / Prefer not to say), both required, saved on each of the participant's rows. "Under 18" ends the study politely and saves nothing (consent is 18+).
- A group is only assigned when all three of its videos have links, so missing videos never reach participants.

## Videos
`VIDEOS` in app.py, code = business letter + number: 1 F22, 2 F28, 3 F35, 4 M22, 5 M28, 6 M35 (e.g. A4 = business A, male voice, age 22).
YouTube titles must show only the neutral code ("Pitch A4"): the embedded player can show the title. Give each video's length in seconds; "Continue" works after 90% of it.

## Google Sheet
1. Create an empty Google Sheet, open Extensions > Apps Script, paste `apps_script/Code.gs`.
2. Deploy > New deployment > Web app; Execute as: Me; Who has access: Anyone. Copy the web app URL.
3. In Streamlit Cloud: app settings > Secrets, add `SHEET_URL = "https://script.google.com/macros/s/.../exec"`.
   Locally: put the same line in `.streamlit/secrets.toml` (gitignored).
Without `SHEET_URL` the app is in test mode: nothing is saved and the answers are shown on screen.
The Sheet gets `responses` (one row per participant per pitch), `raw` (backup). (The `bonus` tab in Code.gs is no longer used: the bonus draw was removed.)

## Run locally
`pip install -r requirements.txt && streamlit run app.py` (from this folder). Add `?cell=O2-F` to the URL to force a group when piloting.
