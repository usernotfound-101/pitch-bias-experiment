"""Pitch evaluation study (side study T070): the whole participant flow in one Streamlit app.

Flow: consent -> intro -> 3 x (watch pitch video -> invest yes/no + optional question pick
-> 2 conjunction items on their own screen) -> short ending (incl. age group, gender) -> save -> debrief.

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

# Investment decision. The founders' asks are in lakhs, so no rupee amount: a Shark Tank style choice.
# Stored code -> text shown (always in this order: it is an ordered scale).
INVEST_OPTIONS = {
    "yes": "Yes",
    "yes_lower": "Yes, but at a lower valuation than the founder asked for",
    "no": "No",
}

# Extra items (lecture "Conjunction Fallacy"), asked after every pitch, about that pitch.
# Conjunction fallacy: each item offers a single event, that event AND another one, and the opposite
# of the single event. Choosing the conjunction is the fallacy (it can never be more likely than the
# single event). Option order is shuffled per participant and pitch.
CF_ITEMS = {
    "cf_business": ("Think about this business. Which is more likely?",
                    "It is still running in 3 years.",
                    "It is still running in 3 years and has expanded to another state.",
                    "It is no longer running in 3 years."),
    "cf_founder": ("Think about this founder. Which is more likely?",
                   "Within 5 years, the founder steps back from running the business.",
                   "Within 5 years, the founder steps back from running the business to focus on family.",
                   "Within 5 years, the founder is still running the business."),
}

# Participant questions at the end (anonymous; each has an opt-out). Under 18 ends the study unsaved.
AGE_GROUPS = ["Under 18", "18-24", "25-34", "35-44", "45-54", "55 or older", "Prefer not to say"]
GENDERS = ["Woman", "Man", "Non-binary", "Prefer to self-describe", "Prefer not to say"]

MIN_WATCH_SHARE = 0.9  # Continue works once this share of the video length has passed
CONTACT = "ayush.moharana@students.iiit.ac.in"


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
            you answer a few quick questions by tapping. At the end we ask your age group and
            gender. It takes about 7 minutes.<br><br>
            <strong>Your rights</strong><br>
            • Taking part is voluntary. You can stop at any time by closing the page.<br>
            • Your answers are anonymous and stored under a random code. We never ask for your name,
            email or any ID. Age group and gender each have a "Prefer not to say" option.<br>
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
            2. Decide whether you would invest in the business.<br>
            3. If you like, pick the question you would most want to ask the founder (optional).<br>
            4. Answer two quick questions about the business and its founder.<br><br>
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
        "Would you invest in this business?",
        list(INVEST_OPTIONS), index=None, format_func=INVEST_OPTIONS.get, key=f"invest_{i}",
    )
    picked = st.radio(
        "Optional: which question would you most want to ask this founder? You can skip this one.",
        range(4), index=None, format_func=lambda k: options[k][1], key=f"pick_{i}",
    )
    if st.button("Continue", type="primary", use_container_width=True):
        if invest is None:
            st.warning("Please answer whether you would invest. Only the second question is optional.")
        else:
            # Kept until the conjunction screen is done (widget values vanish once the screen changes).
            ss[f"pitch_answer_{i}"] = {
                "pitch_position": i + 1,
                "business": business,
                "founder_age": age,
                "video_code": code,
                "watch_seconds": ss[f"watch_seconds_{i}"],
                "invest_decision": invest,  # yes / yes_lower / no
                "question_focus": options[picked][0] if picked is not None else "skipped",
                "question_text": options[picked][1] if picked is not None else "",
                "options_shown": " | ".join(f"{f}:{t}" for f, t in options),
            }
            go(f"cf_{i}")

elif ss.step.startswith("cf_"):
    # Conjunction items on their own screen, AFTER the question pick, so the founder item
    # ("steps back ... to focus on family") cannot prime which question people pick.
    i = int(ss.step.split("_")[1])
    cf_key = f"cf_order_{i}"
    if cf_key not in ss:  # shuffle conjunction options once per pitch, keep the order on reruns
        ss[cf_key] = {k: random.sample(["single", "conjunction", "other"], k=3) for k in CF_ITEMS}
    st.subheader(f"Pitch {i + 1} of 3: two quick questions")
    cf = {}
    for k, (q, single, conj, other) in CF_ITEMS.items():
        text = {"single": single, "conjunction": conj, "other": other}
        cf[k] = st.radio(q, ss[cf_key][k], index=None, format_func=lambda o, t=text: t[o], key=f"{k}_{i}")
    if st.button("Continue", type="primary", use_container_width=True):
        if None in cf.values():
            st.warning("Please answer both questions.")
        else:
            ss.answers.append({
                **ss[f"pitch_answer_{i}"],
                "cf_business": cf["cf_business"],  # single / conjunction / other; 'conjunction' = fallacy
                "cf_founder": cf["cf_founder"],
                "cf_business_order": "|".join(ss[cf_key]["cf_business"]),  # options as shown, top to bottom
                "cf_founder_order": "|".join(ss[cf_key]["cf_founder"]),
            })
            go(f"video_{i + 1}" if i < 2 else "about")

elif ss.step == "about":
    st.subheader("Last few questions")
    voice_check = st.radio("In the three pitches, the founders' voices were…",
                           ["All female", "All male", "Some female, some male", "Not sure"], index=None)
    invested = st.radio("Have you ever invested money in stocks, mutual funds or a business?",
                        ["Yes", "No"], index=None, horizontal=True)
    age_group = st.radio("Your age group", AGE_GROUPS, index=None)
    gender = st.radio("Your gender", GENDERS, index=None)
    gender_self = ""
    if gender == "Prefer to self-describe":
        gender_self = st.text_input("Optional: your gender in your own words", max_chars=40, key="gender_self")
    if st.button("Submit my answers", type="primary", use_container_width=True):
        if None in (voice_check, invested, age_group, gender):
            st.warning("Please answer every question (each has an option you can choose instead of answering).")
        elif age_group == "Under 18":
            ss.answers = []  # consent was for 18+ only: nothing is saved
            go("under18")
        else:
            common = {
                "participant_id": ss.pid,
                "group": f"{ss.order}-{ss.voice}",
                "order": ss.order,
                "voice": ss.voice,
                "cell_source": ss.cell_source,
                "voice_check": voice_check,
                "participant_age_group": age_group,
                "participant_gender": gender,
                "participant_gender_self": gender_self.strip() if gender == "Prefer to self-describe" else "",
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

elif ss.step == "under18":
    st.info("Thank you for your interest. This study is only for people aged 18 or older, "
            "so your answers have not been saved. You can close this page.")

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
            We are testing whether a founder's voice (male or female) and stated age change whether
            people would invest, how they judge the business and founder, and which questions they
            would ask. The three pitches were adapted from real
            Shark Tank India startups, and each was recorded with different voices and ages.
            Please don't discuss the study with anyone who might still take part.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="box">
            <strong>Questions or concerns?</strong><br>
            If you have any questions about this study, or want to know more about it, contact
            {CONTACT}. You can now close this page.
        </div>
        """,
        unsafe_allow_html=True,
    )
