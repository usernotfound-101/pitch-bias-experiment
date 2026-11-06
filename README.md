streamlit website for our project, looking at the code is akin to cheating :]

## Design
Each visitor is randomly assigned one of 18 videos: 3 pitches x founder gender (male/female) x founder age (22/28/35). The assignment is fixed for the session and passed to the survey as URL parameters (video, pitch, gender, age). Video links are placeholders in app.py (VIDEOS dict) until the real ones are pasted in.

Run locally: `pip install -r requirements.txt && streamlit run app.py` (from this folder).
