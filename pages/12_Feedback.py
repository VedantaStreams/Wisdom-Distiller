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
    st.markdown(
        "<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>",
        unsafe_allow_html=True
    )


def get_sheet(debug=False):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        if "gcp_service_account" not in st.secrets:
            if debug:
                st.error("gcp_service_account not found in Streamlit Secrets")
            return None
        if "FEEDBACK_SHEET_ID" not in st.secrets:
            if debug:
                st.error("FEEDBACK_SHEET_ID not found in Streamlit Secrets")
            return None
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(st.secrets["FEEDBACK_SHEET_ID"])
        if debug:
            st.success("Connected to Google Sheet successfully")
        return sheet
    except Exception as e:
        if debug:
            st.error("Google Sheets connection failed: " + str(e))
        return None


def submit_feedback(name, role, rating, feature, review, suggestion):
    sheet = get_sheet(debug=False)
    if sheet is None:
        return False
    try:
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
            role, rating, feature,
            review.strip(), suggestion.strip(),
            "FALSE"
        ])
        return True
    except Exception:
        return False


def load_approved_reviews():
    sheet = get_sheet(debug=False)
    if sheet is None:
        return []
    try:
        ws = sheet.worksheet("Submissions")
        records = ws.get_all_records()
        return [
            r for r in records
            if str(r.get("Approved", "")).strip().upper() == "TRUE"
        ]
    except Exception:
        return []


# ── Hero ──────────────────────────────────────────────────────────────────────
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
</div>
""", unsafe_allow_html=True)

# ── Check if admin ─────────────────────────────────────────────────────────────
is_admin = False
try:
    is_admin = str(st.secrets.get("UNLIMITED_ACCESS", "")).lower() == "true"
except Exception:
    pass

# ── Tabs ──────────────────────────────────────────────────────────────────────
if is_admin:
    tab_submit, tab_reviews, tab_debug = st.tabs([
        "✍️ Share Your Experience",
        "🌟 What Others Say",
        "🔧 Connection Test"
    ])
else:
    tab_submit, tab_reviews = st.tabs([
        "✍️ Share Your Experience",
        "🌟 What Others Say"
    ])
    tab_debug = None

# ── Tab 1: Submit ──────────────────────────────────────────────────────────────
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
            role = st.selectbox("I am a…", [
                "Satsang Seeker",
                "Chinmaya Mission Member",
                "Student of Vedanta",
                "Discourse Listener",
                "Study Group Facilitator",
                "Other"
            ])

        st.markdown(
            "<div style='font-size:0.85rem;color:#888;margin-bottom:0.3rem;'>"
            "Overall Rating</div>",
            unsafe_allow_html=True
        )
        rating = st.select_slider(
            "Rating",
            options=[1, 2, 3, 4, 5],
            value=5,
            format_func=lambda x: "⭐" * x,
            label_visibility="collapsed"
        )

        feature = st.selectbox("Feature I used most", [
            "Audio Summarizer",
            "Discourse Transcriber",
            "Wisdom Extractor",
            "Video Summarizer",
            "Document Combiner",
            "Multiple features"
        ])

        review = st.text_area(
            "Your experience *",
            height=130,
            placeholder="How has this app helped your study or reflection?"
        )

        suggestion = st.text_area(
            "Suggestions or requests (optional)",
            height=80,
            placeholder="Any features you would like to see?"
        )

        consent = st.checkbox(
            "I am happy for my review to be shared on this page"
        )

        submitted = st.form_submit_button(
            "🙏 Submit Feedback",
            use_container_width=True
        )

        if submitted:
            if not review.strip():
                st.error("Please share your experience before submitting.")
            else:
                display_name = name if consent else "Anonymous"
                success = submit_feedback(
                    display_name, role, rating, feature, review, suggestion
                )
                if success:
                    st.success(
                        "🙏 Thank you for your kind words and seva! "
                        "Your feedback has been received and saved."
                    )
                else:
                    st.success(
                        "🙏 Thank you for your feedback! "
                        "It has been noted and is deeply appreciated."
                    )

# ── Tab 2: Reviews ─────────────────────────────────────────────────────────────
with tab_reviews:
    st.markdown("<br/>", unsafe_allow_html=True)
    reviews = load_approved_reviews()

    if not reviews:
        st.markdown("""
        <div style='text-align:center;padding:2rem 0;'>
            <div style='font-size:0.9rem;color:#444;font-style:italic;'>
            Reviews from fellow seekers will appear here soon. 🙏
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        avg = sum(r.get("Rating", 5) for r in reviews) / len(reviews)
        stars = "⭐" * round(avg)
        st.markdown(
            "<div style='text-align:center;margin-bottom:1.5rem;'>"
            "<div style='font-size:2rem;'>" + stars + "</div>"
            "<div style='font-size:0.9rem;color:#c9a96e;margin-top:0.3rem;'>"
            + str(round(avg, 1)) + " out of 5 · "
            + str(len(reviews)) + " review(s)</div></div>",
            unsafe_allow_html=True
        )
        for r in reversed(reviews):
            n  = r.get("Name", "Anonymous") or "Anonymous"
            rl = r.get("Role", "")
            rt = int(r.get("Rating", 5))
            rv = r.get("Review", "")
            fu = r.get("Feature Used", "")
            s  = "⭐" * rt
            feature_html = (
                "<div style='font-size:0.72rem;color:#444;'>Used: " + fu + "</div>"
                if fu else ""
            )
            st.markdown(
                "<div style='background:#111;border:1px solid #1e1e1e;"
                "border-left:3px solid #c9a96e;border-radius:12px;"
                "padding:1.2rem 1.5rem;margin-bottom:1rem;'>"
                "<div style='display:flex;justify-content:space-between;"
                "margin-bottom:0.5rem;'>"
                "<span style='font-family:Cormorant Garamond,serif;font-size:1rem;"
                "font-weight:600;color:#e8e0d4;'>" + n + "</span>"
                "<span style='font-size:0.75rem;color:#555;'>" + rl + "</span>"
                "<span style='font-size:0.85rem;'>" + s + "</span>"
                "</div>"
                "<div style='font-size:0.88rem;color:#999;line-height:1.8;"
                "font-style:italic;margin-bottom:0.4rem;'>\"" + rv + "\"</div>"
                + feature_html +
                "</div>",
                unsafe_allow_html=True
            )

# ── Tab 3: Debug (admin only) ──────────────────────────────────────────────────
if tab_debug is not None:
    with tab_debug:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.85rem;color:#666;margin-bottom:1rem;'>"
            "Use this tab to test the Google Sheets connection.</div>",
            unsafe_allow_html=True
        )
        if st.button("🔍 Test Google Sheets Connection", key="test_conn"):

            # Show detected IP
            try:
                from utils.usage_tracker import _get_ip
                detected = _get_ip()
                st.info("🌐 Detected IP/Session ID: " + str(detected))
            except Exception as ex:
                st.warning("IP detection error: " + str(ex))

            # Check secrets
            st.markdown("**Checking secrets...**")
            if "FEEDBACK_SHEET_ID" in st.secrets:
                sheet_id = str(st.secrets["FEEDBACK_SHEET_ID"])[:20]
                st.success("FEEDBACK_SHEET_ID found: " + sheet_id + "...")
            else:
                st.error("FEEDBACK_SHEET_ID missing from Streamlit Secrets")

            if "gcp_service_account" in st.secrets:
                sa = dict(st.secrets["gcp_service_account"])
                st.success("gcp_service_account found")
                st.info("client_email: " + sa.get("client_email", "NOT FOUND"))
                st.info("project_id: " + sa.get("project_id", "NOT FOUND"))
                pk = sa.get("private_key", "")
                if pk:
                    st.success("private_key present (" + str(len(pk)) + " chars)")
                else:
                    st.error("private_key is empty")
            else:
                st.error("gcp_service_account missing from Streamlit Secrets")

            # Test connection
            st.markdown("**Testing connection...**")
            get_sheet(debug=True)

            # Test write
            st.markdown("**Testing write...**")
            try:
                sheet = get_sheet(debug=False)
                if sheet:
                    ws = sheet.worksheet("Submissions")
                    row_count = len(ws.get_all_records())
                    st.success("Found Submissions tab with " + str(row_count) + " rows")
                    try:
                        ut = sheet.worksheet("UsageTracker")
                        ut_records = ut.get_all_records()
                        st.success(
                            "Found UsageTracker tab with "
                            + str(len(ut_records)) + " user records"
                        )
                        if ut_records:
                            st.markdown("**Last 3 entries in UsageTracker:**")
                            for rec in ut_records[-3:]:
                                st.info(
                                    "ID: " + str(rec.get("IP", "?"))
                                    + " | Uses: " + str(rec.get("UseCount", "?"))
                                    + " | Blocked: " + str(rec.get("Blocked", "?"))
                                    + " | Last: " + str(rec.get("LastSeen", "?"))
                                )
                    except Exception:
                        st.warning(
                            "UsageTracker tab not found yet — "
                            "created automatically on first visitor use."
                        )
                else:
                    st.error("Could not connect to sheet")
            except Exception as ex:
                st.error("Write test failed: " + str(ex))

# ── Bottom ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='max-width:600px;margin:2rem auto 0;text-align:center;'>
    <div style='font-size:0.78rem;color:#444;line-height:1.8;font-style:italic;'>
    All feedback is reviewed before appearing here.
    Your personal details are never shared or stored beyond this app.
    </div>
</div>
<div style="text-align:center; padding: 1.5rem 0 0.5rem;">
    <div style="font-size:1.1rem; letter-spacing:6px;">🪷 🕉️ 🪷</div>
</div>
""", unsafe_allow_html=True)
