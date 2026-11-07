streamlit website for our project, looking at the code is akin to cheating :]

## Design
Side study T070 (CLAUDE.md, "Side study"). One Streamlit app runs the whole flow:
consent -> 3 pitch videos, each followed by 2 tap questions -> 4 short closing questions -> save -> debrief with the contact for questions.

- 6 groups = 3 orders (O1-O3) x founder voice (F or M, the same for all three pitches), assigned at random.
- Each order shows businesses A, B and C once; across the orders every business appears once at each age (22, 28, 35).
- Per pitch: invest ₹0-1,000 (tap, steps of 100) and pick the question you would most want to ask (2 promotion and 2 prevention options, shuffled).
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
