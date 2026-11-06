"""Pitch evaluation study (side study T070): the whole participant flow in one Streamlit app.

Flow: consent -> intro -> 3 x (watch pitch video -> 2 tap questions) -> short ending -> save -> debrief.

Design: 6 groups = 3 orders x founder voice (F or M, the same for all three pitches).
Each order shows the three businesses A, B and C once, and across the three orders every
business appears once at each founder age (22, 28, 35), so age is never tied to one business.

Answers go to a Google Sheet through the Apps Script web app in apps_script/Code.gs.
Its URL is read from Streamlit secrets (SHEET_URL), never committed. Without it the app
runs in test mode: nothing is saved and the rows are shown on screen instead.
"""
import json
import random
import time
import urllib.request
import uuid
from datetime import datetime, timezone

import streamlit as st

st.set_page_config(
    page_title="Startup Pitch Study",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Videos. Code = business letter + number: 1 F22, 2 F28, 3 F35, 4 M22, 5 M28, 6 M35.
# YouTube titles must show only this neutral code ("Pitch A4"), never gender, age or name.
# Each entry: (YouTube link, video length in seconds). Empty link = not uploaded yet.
# ---------------------------------------------------------------------------
VIDEO_NUMBER = {("F", 22): 1, ("F", 28): 2, ("F", 35): 3, ("M", 22): 4, ("M", 28): 5, ("M", 35): 6}

VIDEOS = {
    "A1": ("https://youtu.be/iQGWwFgKuDs", 80),
    "A2": ("https://youtu.be/xWAmQykrazY", 67),
    "A3": ("https://youtu.be/BHinJR1bkjM", 65),
    "A4": ("https://youtu.be/XQG25VvfUSQ", 75),
    "A5": ("https://youtu.be/-mOqK6nFcvQ", 75),
    "A6": ("https://youtu.be/GumIyxtpMAk", 75),
    "B1": ("https://youtu.be/XzqYBezWw_8", 76),
    "B2": ("https://youtu.be/Phpfscp3cp0", 67),
    "B3": ("https://youtu.be/vihuNacDaYI", 68),
    "B4": ("https://youtu.be/cOHvzunlLmk", 79),
    "B5": ("https://youtu.be/V-kaZ5LOI50", 79),
    "B6": ("https://youtu.be/gSicFKxv-wA", 79),
    "C1": ("https://youtu.be/-zT1HFi44nY", 61),
    "C2": ("https://youtu.be/QbEKEhS1xxQ", 53),
    "C3": ("https://youtu.be/sRwg4oFtMDE", 61),
    "C4": ("https://youtu.be/YaVE3Sx-O_0", 69),
    "C5": ("https://youtu.be/1n9Bd38njAo", 69),
    "C6": ("https://youtu.be/st754wRZaf8", 69),
}

# Orders: (business, founder age) for pitch 1, 2 and 3.
ORDERS = {
    "O1": [("A", 22), ("B", 28), ("C", 35)],
    "O2": [("B", 35), ("C", 22), ("A", 28)],
    "O3": [("C", 28), ("A", 35), ("B", 22)],
}
VOICES = ["F", "M"]

# Per business: two promotion (growth, gains) and two prevention (risks, losses) questions,
# following the project codebook. Shown in random order; we record which one is picked.
QUESTION_OPTIONS = {
    "A": [
        ("promotion", "How will you expand beyond Jammu and Kashmir?"),
        ("promotion", "How many more sellers and platforms can you sign up next year?"),
        ("prevention", "What happens if a big courier company starts serving these towns?"),
        ("prevention", "Is the business profitable yet, or are you burning cash?"),
    ],
    "B": [
        ("promotion", "How big can this brand grow, in India and abroad?"),
        ("promotion", "Which new toys or product lines will you launch next?"),
        ("prevention", "What if a large toy brand starts selling cheaper copies?"),
        ("prevention", "Can the artisans keep quality steady if orders grow fast?"),
    ],
    "C": [
        ("promotion", "How quickly can you get into stores in other states?"),
        ("promotion", "Which new flavours or products will drive your next stage of growth?"),
        ("prevention", "What happens to your costs if the banana harvest is poor?"),
        ("prevention", "How will you stop big snack brands from copying you?"),
    ],
}

INVEST_CHOICES = list(range(0, 1001, 100))  # rupees, tapped not typed
MIN_WATCH_SHARE = 0.9  # Continue works once this share of the video length has passed
CONTACT = "STUDY_CONTACT_EMAIL"  # replace with the team's study email


def video_code(business, voice, age):
    return f"{business}{VIDEO_NUMBER[(voice, age)]}"


def group_ready(order, voice):
    """A group can be assigned only when all three of its videos are uploaded."""
    return all(VIDEOS[video_code(b, voice, a)][0] for b, a in ORDERS[order])


def sheet_url():
    try:
        return st.secrets.get("SHEET_URL", "")
    except Exception:  # no secrets file at all
        return ""


def post_json(payload):
    """POST to the Apps Script web app. Returns True if it answered ok."""
    req = urllib.request.Request(
        sheet_url(),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "text/plain;charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8")).get("ok", False)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 760px;}
        .box {background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px;
              padding: 1.25rem; margin-bottom: 1.5rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

ss = st.session_state
TEST_MODE = not sheet_url()

# ---------------------------------------------------------------------------
# Assignment (once per session)
# ---------------------------------------------------------------------------
if "pid" not in ss:
    params = st.query_params
    ss.pid = params.get("pid") or uuid.uuid4().hex[:10]
    ready = [(o, v) for o in ORDERS for v in VOICES if group_ready(o, v)]
    forced = (params.get("cell") or "").upper().replace(" ", "-")  # e.g. ?cell=O2-F for piloting
    if forced and forced.count("-") == 1 and tuple(forced.split("-")) in ready:
        ss.order, ss.voice = forced.split("-")
        ss.cell_source = "url"
    elif ready:
        ss.order, ss.voice = random.choice(ready)
        ss.cell_source = "random"
    else:
        ss.order = ss.voice = None
    ss.step = "consent"
    ss.answers = []  # one dict per pitch
    ss.started_at = datetime.now(timezone.utc).isoformat()

if ss.order is None:
    st.title("Startup Pitch Study")
    st.info("This study is not open yet. Please check back later.")
    st.stop()

PITCHES = [(b, a, video_code(b, ss.voice, a)) for b, a in ORDERS[ss.order]]

if TEST_MODE:
    st.caption(f"Test mode: answers are not saved. Group {ss.order}-{ss.voice}.")


def go(step):
    ss.step = step
    st.rerun()


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------
st.title("Startup Pitch Study")

if ss.step == "consent":
    st.markdown(
        f"""
        <div class="box">
            <strong>About this study</strong><br>
            This is a student research project for a Neuroeconomics course at IIIT Hyderabad.
            You will watch three short startup pitches (about one minute each). After each one
            you answer two quick questions by tapping. It takes about 6 minutes.<br><br>
            <strong>Your rights</strong><br>
            • Taking part is voluntary. You can stop at any time by closing the page.<br>
            • Your answers are anonymous and stored under a random code. We do not ask for your name.<br>
            • At the end you may enter a bonus draw by leaving an email or phone number. This is optional,
              stored separately, and cannot be linked to your answers.<br>
            • Answers are used only for this course project and reported only as group totals.<br>
            • You must be 18 or older to take part.<br><br>
            Questions? Contact: {CONTACT}
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    if c1.button("I am 18+ and agree to take part", type="primary", use_container_width=True):
        go("intro")
    if c2.button("I do not want to take part", use_container_width=True):
        go("declined")

elif ss.step == "declined":
    st.info("Thank you for your time. You did not take part, and nothing was recorded. You can close this page.")

elif ss.step == "intro":
    st.markdown(
        """
        <div class="box">
            Imagine you are an investor. For each of the three businesses:<br>
            1. Watch the founder's pitch once, all the way through, with the sound on.<br>
            2. Decide how much of ₹1,000 you would invest.<br>
            3. Pick the question you would most want to ask the founder.<br><br>
            Please use headphones or turn your sound up.
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Start the first pitch", type="primary", use_container_width=True):
        go("video_0")

elif ss.step.startswith("video_"):
    i = int(ss.step.split("_")[1])
    business, age, code = PITCHES[i]
    url, length = VIDEOS[code]
    shown_key = f"video_shown_{i}"
    if shown_key not in ss:
        ss[shown_key] = time.time()
    st.subheader(f"Pitch {i + 1} of 3")
    st.write("Watch the whole pitch once. The questions open after it.")
    st.video(url)
    if st.button("I have watched the whole pitch", type="primary", use_container_width=True):
        watched = time.time() - ss[shown_key]
        if watched < MIN_WATCH_SHARE * length:
            st.warning("The pitch is not over yet. Please watch it to the end, then press the button again.")
        else:
            ss[f"watch_seconds_{i}"] = round(watched, 1)
            go(f"questions_{i}")

elif ss.step.startswith("questions_"):
    i = int(ss.step.split("_")[1])
    business, age, code = PITCHES[i]
    opt_key = f"options_{i}"
    if opt_key not in ss:  # shuffle once, keep the order on reruns
        ss[opt_key] = random.sample(QUESTION_OPTIONS[business], k=4)
    options = ss[opt_key]
    st.subheader(f"Pitch {i + 1} of 3: your decision")
    invest = st.radio(
        "You have ₹1,000 for this pitch. How much would you invest in this founder? (Anything you don't invest, you keep.)",
        INVEST_CHOICES, index=None, horizontal=True, format_func=lambda x: f"₹{x}", key=f"invest_{i}",
    )
    picked = st.radio(
        "Which question would you most want to ask this founder?",
        range(4), index=None, format_func=lambda k: options[k][1], key=f"pick_{i}",
    )
    if st.button("Continue", type="primary", use_container_width=True):
        if invest is None or picked is None:
            st.warning("Please answer both questions.")
        else:
            ss.answers.append({
                "pitch_position": i + 1,
                "business": business,
                "founder_age": age,
                "video_code": code,
                "watch_seconds": ss[f"watch_seconds_{i}"],
                "invest_rupees": invest,
                "question_focus": options[picked][0],
                "question_text": options[picked][1],
                "options_shown": " | ".join(f"{f}:{t}" for f, t in options),
            })
            go(f"video_{i + 1}" if i < 2 else "about")

elif ss.step == "about":
    st.subheader("Last few questions")
    voice_check = st.radio("In the three pitches, the founders' voices were…",
                           ["All female", "All male", "Some female, some male", "Not sure"], index=None)
    age_band = st.radio("Your age", ["18-20", "21-24", "25-34", "35 or older"], index=None, horizontal=True)
    gender = st.radio("Your gender", ["Female", "Male", "Other", "Prefer not to say"], index=None, horizontal=True)
    invested = st.radio("Have you ever invested money in stocks, mutual funds or a business?",
                        ["Yes", "No"], index=None, horizontal=True)
    if st.button("Submit my answers", type="primary", use_container_width=True):
        if None in (voice_check, age_band, gender, invested):
            st.warning("Please answer every question.")
        else:
            common = {
                "participant_id": ss.pid,
                "group": f"{ss.order}-{ss.voice}",
                "order": ss.order,
                "voice": ss.voice,
                "cell_source": ss.cell_source,
                "voice_check": voice_check,
                "participant_age_band": age_band,
                "participant_gender": gender,
                "invested_before": invested,
                "started_at": ss.started_at,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "test_mode": int(TEST_MODE),
            }
            rows = [{**common, **a} for a in ss.answers]
            columns = list(rows[0].keys())
            ss.rows = rows
            ss.saved = TEST_MODE or post_json({
                "type": "response",
                "columns": columns,
                "rows": [[r[c] for c in columns] for r in rows],
                "raw": {"pid": ss.pid, "rows": rows},
            })
            go("done")

elif ss.step == "done":
    if not ss.saved:
        st.error("Your answers could not be sent. Please copy the text below and send it to the research team.")
        st.code(json.dumps(ss.rows))
    else:
        st.success("Thank you for taking part.")
    if TEST_MODE:
        st.dataframe(ss.rows)
    st.markdown(
        """
        <div class="box">
            <strong>What this study was about</strong><br>
            We are testing whether a founder's voice (male or female) and stated age change how much
            people invest and which questions they would ask. The three pitches were adapted from real
            Shark Tank India startups, and each was recorded with different voices and ages.
            Please don't discuss the study with anyone who might still take part.
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not ss.get("bonus_done"):
        st.markdown("**Enter the bonus draw (optional).** Leave an email or phone number. It is stored "
                    "separately from your answers and used only to contact the winner.")
        contact = st.text_input("Email or phone", max_chars=200)
        if st.button("Enter the draw") and contact.strip():
            ok = TEST_MODE or post_json({"type": "bonus", "contact": contact.strip(),
                                         "at": datetime.now(timezone.utc).isoformat()})
            ss.bonus_done = True
            st.success("You are in the draw." if ok else "Sorry, that did not go through. Please email us instead.")
