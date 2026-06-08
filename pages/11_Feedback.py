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
def get_sheet(debug=False):
    """Connect to Google Sheet using service account credentials from secrets."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        # Check secrets exist
        if "gcp_service_account" not in st.secrets:
            if debug: st.error("❌ gcp_service_account not found in Streamlit Secrets")
            return None
        if "FEEDBACK_SHEET_ID" not in st.secrets:
            if debug: st.error("❌ FEEDBACK_SHEET_ID not found in Streamlit Secrets")
            return None

        creds_dict = dict(st.secrets["gcp_service_account"])

        # Fix private_key newlines — common issue with Streamlit secrets
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds  = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet  = client.open_by_key(st.secrets["FEEDBACK_SHEET_ID"])
        if debug: st.success("✅ Connected to Google Sheet successfully")
        return sheet
    except Exception as e:
        if debug: st.error(f"❌ Google Sheets connection failed: {e}")
        return None


def submit_feedback(name: str, role: str, rating: int,
                    feature: str, review: str, suggestion: str):
    """Write a new feedback row to the Submissions sheet."""
    sheet = get_sheet(debug=False)
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
# Show debug tab only to admin (you)
_is_admin = str(st.secrets.get("UNLIMITED_ACCESS", "")).lower() == "true"
if _is_admin:
    tab_submit, tab_reviews, tab_debug = st.tabs(["✍️ Share Your Experience", "🌟 What Others Say", "🔧 Connection Test"])
else:
    tab_submit, tab_reviews = st.tabs(["✍️ Share Your Experience", "🌟 What Others Say"])
    tab_debug = None

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
                        "Your feedback has been received and saved."
                    )
                else:
                    st.warning(
                        "⚠️ Your feedback was received but could not be saved to the sheet. "
                        "Please check the connection below."
                    )
                    # Show debug info
                    with st.expander("🔍 Connection diagnostic"):
                        get_sheet(debug=True)

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

# ── Tab 3: Debug ──────────────────────────────────────────────────────────────
if tab_debug is not None:
 with tab_debug:
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.85rem;color:#666;margin-bottom:1rem;'>"
        "Use this tab to test the Google Sheets connection and diagnose any issues.</div>",
        unsafe_allow_html=True
    )
    if st.button("🔍 Test Google Sheets Connection", key="test_conn"):
        # Show detected IP
        try:
            from utils.usage_tracker import _get_ip
            detected_ip = _get_ip()
            st.info(f"🌐 Detected IP/Session ID: `{detected_ip}`")
        except Exception as e:
            st.warning(f"IP detection: {e}")

        st.markdown("**Checking secrets...**")
        # Check secrets
        if "FEEDBACK_SHEET_ID" in st.secrets:
            st.success(f"✅ FEEDBACK_SHEET_ID found: {st.secrets['FEEDBACK_SHEET_ID'][:20]}...")
        else:
            st.error("❌ FEEDBACK_SHEET_ID missing from Streamlit Secrets")

        if "gcp_service_account" in st.secrets:
            sa = dict(st.secrets["gcp_service_account"])
            st.success(f"✅ gcp_service_account found")
            st.info(f"   client_email: {sa.get('client_email','NOT FOUND')}")
            st.info(f"   project_id: {sa.get('project_id','NOT FOUND')}")
            pk = sa.get('private_key','')
            if pk:
                st.success(f"✅ private_key present ({len(pk)} chars)")
                if "\n" in pk:
                    st.warning("⚠️ private_key contains literal \\n — may need fixing")
                else:
                    st.success("✅ private_key newlines look correct")
            else:
                st.error("❌ private_key is empty")
        else:
            st.error("❌ gcp_service_account missing from Streamlit Secrets")

        st.markdown("**Testing connection...**")
        get_sheet(debug=True)

        st.markdown("**Testing write...**")
        try:
            sheet = get_sheet(debug=False)
            if sheet:
                ws = sheet.worksheet("Submissions")
                st.success(f"✅ Found Submissions tab with {len(ws.get_all_records())} rows")

                # Check UsageTracker tab
                try:
                    ut = sheet.worksheet("UsageTracker")
                    records = ut.get_all_records()
                    st.success(f"✅ Found UsageTracker tab with {len(records)} user records")
                    if records:
                        st.markdown("**Last 3 entries in UsageTracker:**")
                        for r in records[-3:]:
                            st.info(
                                f"ID: `{r.get('IP','?')}` · "
                                f"Uses: `{r.get('UseCount','?')}` · "
                                f"Blocked: `{r.get('Blocked','?')}` · "
                                f"Last seen: `{r.get('LastSeen','?')}`"
                            )
                except Exception:
                    st.warning(
                        "⚠️ UsageTracker tab not found yet — "
                        "it will be created automatically when the first "
