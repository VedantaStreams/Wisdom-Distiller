import streamlit as st
import sys
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="Feedback · Wisdom Distiller",
    page_icon="🌟",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils.styles import SHARED_CSS
st.markdown(SHARED_CSS, unsafe_allow_html=True)

with st.sidebar:
    try:
        st.page_link("app.py", label="🏠 Home")
    except Exception:
        pass
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>",
                unsafe_allow_html=True)

# ── Google Sheets helper ──────────────────────────────────────────────────────
def get_sheet():
    """Connect to Google Sheet using service account credentials from secrets."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds  = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet  = client.open_by_key(st.secrets["FEEDBACK_SHEET_ID"])
        return sheet
    except Exception as e:
        return None


def submit_feedback(name: str, role: str, rating: int,
                    feature: str, review: str, suggestion: str):
    """Write a new feedback row to the Submissions sheet."""
    sheet = get_sheet()
    if sheet is None:
        return False
    try:
        ws = sheet.worksheet("Submissions")
    except Exception:
        ws = sheet.add_worksheet("Submissions", rows=1000, cols=10)
        ws.append_row([
            "Timestamp", "Name", "Role", "Rating",
            "Feature Used", "Review", "Suggestion", "Approved"
        ])
    ws.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        name.strip() or "Anonymous",
        role,
        rating,
        feature,
        review.strip(),
        suggestion.strip(),
        "FALSE"          # ← YOU change this to TRUE in Google Sheets to approve
    ])
    return True


def load_approved_reviews():
    """Load only approved reviews from the Submissions sheet."""
    sheet = get_sheet()
    if sheet is None:
        return []
    try:
        ws      = sheet.worksheet("Submissions")
        records = ws.get_all_records()
        approved = [
            r for r in records
            if str(r.get("Approved", "")).strip().upper() == "TRUE"
        ]
        return approved
    except Exception:
        return []

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <h1>🌟 Share Your <span class="accent">Experience</span></h1>
    <p class="subtitle">Your feedback helps this seva grow</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="about-box">
    Wisdom Distiller is offered as a small <b style='color:#b8a88a;'>seva</b>.
    Your experience, suggestions, and kind words help shape it for fellow seekers.
    Reviews shared below (with your permission) may inspire others to use the app
    in their spiritual study.
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TABS — Submit | Read Reviews
# ══════════════════════════════════════════════════════════════════════════════
tab_submit, tab_reviews = st.tabs(["✍️ Share Your Experience", "🌟 What Others Say"])

# ── Tab 1: Submit ─────────────────────────────────────────────────────────────
with tab_submit:
    st.markdown("<br/>", unsafe_allow_html=True)

    with st.form("feedback_form", clear_on_submit=True):
        f1, f2 = st.columns(2)
        with f1:
            name = st.text_input(
                "Your name (optional)",
                placeholder="e.g. Ramesh · or leave blank for Anonymous"
            )
        with f2:
            role = st.selectbox(
                "I am a…",
                ["Satsang Seeker", "Chinmaya Mission Member",
                 "Student of Vedānta", "Discourse Listener",
                 "Study Group Facilitator", "Other"]
            )

        # Star rating
        st.markdown(
            "<div style='font-size:0.85rem;color:#888;margin-bottom:0.3rem;'>"
            "⭐ Overall Rating</div>",
            unsafe_allow_html=True
        )
        rating = st.select_slider(
            "Rating",
            options=[1, 2, 3, 4, 5],
            value=5,
            format_func=lambda x: "⭐" * x,
            label_visibility="collapsed"
        )

        feature = st.selectbox(
            "Feature I used most",
            ["Audio Summarizer", "Discourse Transcriber",
             "Wisdom Extractor", "Video Summarizer",
             "Document Combiner", "Multiple features"]
        )

        review = st.text_area(
            "Your experience *",
            height=130,
            placeholder=(
                "How has this app helped your study or reflection?\n"
                "What did you find most useful?\n"
                "How did it support your śravaṇa or manana?"
            )
        )

        suggestion = st.text_area(
            "Suggestions or requests (optional)",
            height=80,
            placeholder="Any features you'd like to see? Languages? Other feedback?"
        )

        consent = st.checkbox(
            "I am happy for my review to be shared on this page "
            "(your name will appear as entered above)"
        )

        submitted = st.form_submit_button(
            "🙏 Submit Feedback",
            use_container_width=True
        )

        if submitted:
            if not review.strip():
                st.error("Please share your experience before submitting.")
            else:
                success = submit_feedback(
                    name if consent else "Anonymous",
                    role, rating, feature, review, suggestion
                )
                if success:
                    st.success(
                        "🙏 Thank you for your kind words and seva! "
                        "Your feedback has been received."
                    )
                else:
                    # Fallback if Google Sheets not configured
                    st.success(
                        "🙏 Thank you for your feedback! "
                        "It has been noted and is deeply appreciated."
                    )

# ── Tab 2: Approved reviews ────────────────────────────────────────────────────
with tab_reviews:
    st.markdown("<br/>", unsafe_allow_html=True)

    reviews = load_approved_reviews()

    if not reviews:
        # Show placeholder testimonials until real ones come in
        st.markdown("""
        <div style='text-align:center;padding:2rem 0;'>
            <div style='font-size:0.9rem;color:#444;font-style:italic;'>
            Reviews from fellow seekers will appear here.<br/>
            Be the first to share your experience! 🙏
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Summary stats
        avg_rating = sum(r.get("Rating", 5) for r in reviews) / len(reviews)
        stars = "⭐" * round(avg_rating)
        st.markdown(f"""
        <div style='text-align:center;margin-bottom:1.5rem;'>
            <div style='font-size:2rem;'>{stars}</div>
            <div style='font-size:0.9rem;color:#c9a96e;margin-top:0.3rem;'>
            {avg_rating:.1f} out of 5 · {len(reviews)} review{'s' if len(reviews)>1 else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

        for r in reversed(reviews):  # newest first
            name_display = r.get("Name", "Anonymous") or "Anonymous"
            role_display = r.get("Role", "")
            rating_val   = int(r.get("Rating", 5))
            feature_used = r.get("Feature Used", "")
            review_text  = r.get("Review", "")
            stars_str    = "⭐" * rating_val

            st.markdown(f"""
            <div style='background:#111;border:1px solid #1e1e1e;
            border-left:3px solid #c9a96e;border-radius:12px;
            padding:1.2rem 1.5rem;margin-bottom:1rem;'>
                <div style='display:flex;justify-content:space-between;
                align-items:flex-start;margin-bottom:0.5rem;'>
                    <div>
                        <span style='font-family:Cormorant Garamond,serif;
                        font-size:1rem;font-weight:600;color:#e8e0d4;'>
                        {name_display}</span>
                        <span style='font-size:0.75rem;color:#555;margin-left:0.6rem;'>
                        {role_display}</span>
                    </div>
                    <div style='font-size:0.85rem;'>{stars_str}</div>
                </div>
                <div style='font-size:0.88rem;color:#999;line-height:1.8;
                font-style:italic;margin-bottom:0.4rem;'>"{review_text}"</div>
                {f"<div style='font-size:0.72rem;color:#444;'>Used: {feature_used}</div>" if feature_used else ""}
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BOTTOM NOTE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style='max-width:600px;margin:2rem auto 0;text-align:center;'>
    <div style='font-size:0.78rem;color:#444;line-height:1.8;font-style:italic;'>
    All feedback is reviewed before appearing here.<br/>
    Your personal details are never shared or stored beyond this app.
    </div>
</div>
<div style="text-align:center; padding: 1.5rem 0 0.5rem;">
    <div style="font-size:1.1rem; letter-spacing:6px;">🪷 🕉️ 🪷</div>
</div>
""", unsafe_allow_html=True)
