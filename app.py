import itertools
import random
from urllib.parse import urlencode

import streamlit as st
import streamlit.components.v1 as components

# --- Page Configuration ---
st.set_page_config(
    page_title="Product Pitch Evaluation Study",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Design: 3 pitches x 2 founder genders x 3 founder ages = 18 videos ---
PITCHES = [1, 2, 3]
GENDERS = ["male", "female"]
AGES = [22, 28, 35]

# One URL per condition, keyed by (pitch, gender, age).
# Replace each placeholder with the real YouTube link or direct MP4 link.
VIDEOS = {
    (1, "male", 22): "https://www.youtube.com/watch?v=P1_MALE_22",
    (1, "male", 28): "https://www.youtube.com/watch?v=P1_MALE_28",
    (1, "male", 35): "https://www.youtube.com/watch?v=P1_MALE_35",
    (1, "female", 22): "https://www.youtube.com/watch?v=P1_FEMALE_22",
    (1, "female", 28): "https://www.youtube.com/watch?v=P1_FEMALE_28",
    (1, "female", 35): "https://www.youtube.com/watch?v=P1_FEMALE_35",
    (2, "male", 22): "https://www.youtube.com/watch?v=P2_MALE_22",
    (2, "male", 28): "https://www.youtube.com/watch?v=P2_MALE_28",
    (2, "male", 35): "https://www.youtube.com/watch?v=P2_MALE_35",
    (2, "female", 22): "https://www.youtube.com/watch?v=P2_FEMALE_22",
    (2, "female", 28): "https://www.youtube.com/watch?v=P2_FEMALE_28",
    (2, "female", 35): "https://www.youtube.com/watch?v=P2_FEMALE_35",
    (3, "male", 22): "https://www.youtube.com/watch?v=P3_MALE_22",
    (3, "male", 28): "https://www.youtube.com/watch?v=P3_MALE_28",
    (3, "male", 35): "https://www.youtube.com/watch?v=P3_MALE_35",
    (3, "female", 22): "https://www.youtube.com/watch?v=P3_FEMALE_22",
    (3, "female", 28): "https://www.youtube.com/watch?v=P3_FEMALE_28",
    (3, "female", 35): "https://www.youtube.com/watch?v=P3_FEMALE_35",
}

# Fail early if a condition is missing or extra, so no visitor gets a broken page.
CONDITIONS = list(itertools.product(PITCHES, GENDERS, AGES))
assert set(VIDEOS) == set(CONDITIONS), "VIDEOS must have exactly one URL per (pitch, gender, age)"

# Replace with your survey link (e.g., Tally, Google Forms, Qualtrics)
BASE_SURVEY_URL = "https://tally.so/r/YOUR_FORM_ID"

# --- Session State Allocation ---
# Draw one of the 18 conditions uniformly at random, and lock it in session
# state so a page rerun does not switch the video.
if "condition" not in st.session_state:
    st.session_state.condition = random.choice(CONDITIONS)

pitch, gender, age = st.session_state.condition
active_video = VIDEOS[(pitch, gender, age)]
video_id = f"p{pitch}_{gender[0]}_{age}"  # e.g. p2_f_28

# Pass the assigned condition to the survey as URL parameters
survey_params = urlencode({"consent": "yes", "video": video_id, "pitch": pitch, "gender": gender, "age": age})
survey_link_with_param = f"{BASE_SURVEY_URL}?{survey_params}"

# --- Custom Styling ---
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 760px;
        }
        .instruction-box {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1.25rem;
            margin-bottom: 1.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- App UI ---
st.title("Startup Pitch Evaluation Study")

# Contact shown on the consent screen. Replace with the team's study email.
CONTACT = "STUDY_CONTACT_EMAIL"

# --- Consent screen: nothing else is shown until the visitor agrees ---
if "consent" not in st.session_state:
    st.session_state.consent = None  # None = not answered, True = agreed, False = declined

if st.session_state.consent is not True:
    if st.session_state.consent is False:
        st.info("Thank you for your time. You did not take part, and nothing was recorded. You can close this page.")
        st.stop()

    st.markdown(
        f"""
        <div class="instruction-box">
            <strong>About this study</strong><br>
            This is a student research project for a Neuroeconomics course at IIIT Hyderabad.
            You will watch one short startup pitch (about 60 seconds) and then answer a few questions
            about the business in a separate form. It takes about 5 minutes.<br><br>
            <strong>Your rights</strong><br>
            • Taking part is voluntary. You can stop at any time by closing the page, with no consequence.<br>
            • Your answers are anonymous: we do not ask for your name, email or any other identifying details.<br>
            • Responses are used only for this course project and reported only as group totals.<br>
            • You must be 18 or older to take part.<br><br>
            Questions? Contact: {CONTACT}
        </div>
        """,
        unsafe_allow_html=True,
    )
    agree_col, decline_col = st.columns(2)
    if agree_col.button("I am 18+ and agree to take part", type="primary", use_container_width=True):
        st.session_state.consent = True
        st.rerun()
    if decline_col.button("I do not want to take part", use_container_width=True):
        st.session_state.consent = False
        st.rerun()
    st.stop()

st.markdown(
    """
    <div class="instruction-box">
        <strong>Instructions:</strong><br>
        1. Watch the 60-second pitch below carefully in its entirety.<br>
        2. Evaluate the business proposition using the survey linked beneath the video.<br>
        3. All responses are completely anonymous.
    </div>
    """,
    unsafe_allow_html=True,
)

# Display the allocated video
st.video(active_video)

st.markdown("---")

# Option A: Outbound Button (Opens survey in a new tab)
st.markdown("### Next Step: Share Your Feedback")
st.write("Once you've finished watching, proceed to the evaluation form:")

st.link_button(
    label="Proceed to Evaluation Form ➔",
    url=survey_link_with_param,
    type="primary",
    use_container_width=True,
)

# Option B: Direct Survey Embed (Uncomment if using an embeddable form like Tally/Google Forms)
# components.iframe(survey_link_with_param, height=650, scrolling=True)
