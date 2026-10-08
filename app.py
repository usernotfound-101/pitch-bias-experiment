import streamlit as st
import random
import streamlit.components.v1 as components

# --- Page Configuration ---
st.set_page_config(
    page_title="Product Pitch Evaluation Study",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Video & Survey Config ---
# Replace these with your actual YouTube embed URLs or direct MP4 links
VIDEO_MALE = "https://www.youtube.com/watch?v=VIDEO_ID_MALE"
VIDEO_FEMALE = "https://www.youtube.com/watch?v=VIDEO_ID_FEMALE"

# Replace with your survey link (e.g., Tally, Google Forms, Qualtrics)
BASE_SURVEY_URL = "https://tally.so/r/YOUR_FORM_ID"

# --- Session State Allocation ---
# Lock the variant in session state so a page rerun does not flip the video
if "variant" not in st.session_state:
    st.session_state.variant = random.choice(["male", "female"])

variant = st.session_state.variant
active_video = VIDEO_MALE if variant == "male" else VIDEO_FEMALE

# Append the assigned group to the survey link as a URL parameter
survey_link_with_param = f"{BASE_SURVEY_URL}?group={variant}"

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