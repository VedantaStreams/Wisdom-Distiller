import streamlit as st
import base64
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.styles import SHARED_CSS

st.set_page_config(
    page_title="Wisdom Distiller · Suma AI Hub",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)

# Nav card button styling
st.markdown("""
<style>
div[data-testid="column"] .stButton > button {
    background: transparent !important;
    color: #c9a96e !important;
    border: 1px solid #c9a96e !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    padding: 0.35rem 1rem !important;
    margin-top: 0.6rem;
    width: 100%;
}
div[data-testid="column"] .stButton > button:hover {
    background: #c9a96e !important;
    color: #0a0a0a !important;
}
</style>
""", unsafe_allow_html=True)


# ── Load images ────────────────────────────────────────────────────────────────
def img_b64(path: str, mime: str = "image/jpeg") -> str:
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"

om_path = Path(__file__).parent / "Om.jpeg"
om_tag = (f'<img class="om" src="{img_b64(str(om_path))}" alt="Om"/>'
          if om_path.exists() else '<div style="font-size:2.5rem">🕉️</div>')

# iPhone home screen icon — served as static file
st.markdown(
    '<link rel="apple-touch-icon" href="./app/static/apple-touch-icon.png">'
    '<link rel="apple-touch-icon-precomposed" href="./app/static/apple-touch-icon.png">',
    unsafe_allow_html=True
)

headshot_path = Path(__file__).parent / "headshot.jpeg"
if headshot_path.exists():
    hs_src = img_b64(str(headshot_path))
    avatar_tag = (
        f'<img src="{hs_src}" alt="Suma Rajashankar"'
        ' style="width:110px;height:110px;border-radius:50%;object-fit:cover;'
        'border:3px solid #c9a96e;display:block;margin:0 auto 0.6rem;'
        'box-shadow:0 0 20px rgba(201,169,110,0.3);"/>'
    )
else:
    avatar_tag = '<div class="bio-avatar-placeholder">SR</div>'

# Try multiple possible filenames for Gurudev photo
gurudev_img = '<div style="font-size:3rem;text-align:center;">🕉️</div>'
for _gd_name in ["gurudev.jpeg", "gurudev.jpg", "Gurudev.jpg", "Gurudev.jpeg"]:
    _gd_path = Path(__file__).parent / _gd_name
    if _gd_path.exists():
        _gd_src = img_b64(str(_gd_path))
        gurudev_img = (
            '<img src="' + _gd_src + '" alt="Pujya Swami Chinmayananda"'
            ' style="width:150px;height:170px;object-fit:cover;object-position:top;'
            'border-radius:10px;border:2px solid #c9a96e;'
            'box-shadow:0 0 24px rgba(201,169,110,0.4);display:block;margin:0 auto;"/>'
        )
        break


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:

    # ── Home button ────────────────────────────────────────────────────────────
    try:
        st.page_link("app.py", label="🏠 Home")
    except Exception:
        pass
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>", unsafe_allow_html=True)

    st.markdown(
        f'<div style="text-align:center; padding:0.8rem 0 0.4rem;">'
        f'{avatar_tag}'
        f'<p style="font-family:Cormorant Garamond,serif; font-size:1.05rem;'
        f' font-weight:600; color:#e8e0d4; margin:0 0 0.15rem;">Suma Rajashankar</p>'
        f'<p style="font-size:0.72rem; color:#c9a96e; letter-spacing:0.4px;'
        f' text-transform:uppercase; margin:0 0 0.5rem;">Senior Research Data Scientist / AI Engineer</p>'
        f'<div style="font-size:0.78rem;">'
        f'<a href="Sadhana_and_Seva" target="_self"'
        f' style="color:#c9a96e; text-decoration:none; border-bottom:1px dashed #c9a96e;">'
        f'✦ Sādhanā &amp; Seva</a></div></div>'
        f'<hr style="border-color:#1e1e1e; margin:0.8rem 0;"/>',
        unsafe_allow_html=True
    )

    # ── API Keys ──────────────────────────────────────────────────────────────
    # Check if keys are pre-loaded via Streamlit Secrets (owner's deployment)
    _secret_anthropic = st.secrets.get("ANTHROPIC_API_KEY", "")
    _secret_openai    = st.secrets.get("OPENAI_API_KEY", "")

    if _secret_anthropic and _secret_openai:
        # Keys are pre-configured — show green badges, no input needed
        anthropic_key = _secret_anthropic
        openai_key    = _secret_openai
        st.markdown("### ⚙️ API Keys")
        st.success("✅ Anthropic key loaded")
        st.success("✅ OpenAI key loaded")
    else:
        # No pre-configured keys — show friendly guided input
        st.markdown("### ⚙️ Enter Your API Keys")
        st.markdown(
            "<div style='background:#111;border:1px solid #2a2a2a;border-left:3px solid #c9a96e;"
            "border-radius:8px;padding:0.8rem 1rem;margin-bottom:0.8rem;font-size:0.78rem;color:#888;line-height:1.7;'>"
            "<b style='color:#c9a96e;'>This app runs on your own API keys.</b><br/>"
            "You will need two keys (a few minutes to set up, pay-as-you-go, "
            "typically just a few cents per discourse).<br/>"
            "Your keys are <b style='color:#b8a88a;'>never stored</b> — they are only used "
            "for your current session and cleared when you close the browser."
            "</div>",
            unsafe_allow_html=True
        )

        # ── Anthropic key ──────────────────────────────────────────────────
        with st.expander("🔑 Step 1 — Get your Anthropic (Claude) key", expanded=False):
            st.markdown(
                "<div style='font-size:0.78rem;color:#888;line-height:1.8;'>"
                "1. Go to <a href='https://console.anthropic.com' target='_blank' "
                "style='color:#c9a96e;'>console.anthropic.com</a><br/>"
                "2. Sign up for a free account<br/>"
                "3. Click <b style='color:#b8a88a;'>API Keys</b> in the left menu<br/>"
                "4. Click <b style='color:#b8a88a;'>Create Key</b> and copy it<br/>"
                "5. Paste it in the box below"
                "</div>",
                unsafe_allow_html=True
            )

        anthropic_key = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-...",
            value=st.session_state.get("anthropic_key", ""),
            help="Starts with sk-ant-  |  Get yours at console.anthropic.com"
        )
        if anthropic_key:
            st.success("✅ Anthropic key entered")
        else:
            st.caption("⬆️ Required for summarization (Claude AI)")

        # ── OpenAI key ─────────────────────────────────────────────────────
        with st.expander("🔑 Step 2 — Get your OpenAI key", expanded=False):
            st.markdown(
                "<div style='font-size:0.78rem;color:#888;line-height:1.8;'>"
                "1. Go to <a href='https://platform.openai.com/api-keys' target='_blank' "
                "style='color:#c9a96e;'>platform.openai.com/api-keys</a><br/>"
                "2. Sign up or log in<br/>"
                "3. Click <b style='color:#b8a88a;'>Create new secret key</b><br/>"
                "4. Copy the key shown (you won't see it again!)<br/>"
                "5. Paste it in the box below"
                "</div>",
                unsafe_allow_html=True
            )

        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            value=st.session_state.get("openai_key", ""),
            help="Starts with sk-  |  Get yours at platform.openai.com"
        )
        if openai_key:
            st.success("✅ OpenAI key entered")
        else:
            st.caption("⬆️ Required for audio transcription (Whisper)")

        if not anthropic_key or not openai_key:
            st.markdown(
                "<div style='background:#111;border:1px solid #2a2a2a;border-radius:8px;"
                "padding:0.6rem 0.8rem;margin-top:0.5rem;font-size:0.75rem;color:#555;"
                "text-align:center;'>Both keys needed to use the app</div>",
                unsafe_allow_html=True
            )

    st.session_state["anthropic_key"] = anthropic_key
    st.session_state["openai_key"]    = openai_key

    st.markdown("---")
    st.markdown(
        "<div style='background:#0d0d0d; border-left:2px solid #c9a96e;"
        " padding:0.8rem 1rem; border-radius:6px; margin-bottom:0.5rem;'>"
        "<div style='font-size:0.78rem; color:#c9a96e; font-weight:500;"
        " margin-bottom:0.5rem;'>🔹 With Reverence and Gratitude</div>"
        "<div style='font-size:0.75rem; color:#777; line-height:1.75; font-style:italic;'>"
        "I offer my humble pran\u0101ms and heartfelt gratitude to "
        "P\u016bjya Swami Apar\u0101jit\u0101nandaj\u012b and "
        "P\u016bjya Sw\u0101m\u012b \u015aara\u1e47\u0101nanda j\u012b. "
        "Their teachings, guidance, and unwavering dedication to the "
        "Guru\u2013\u015ai\u1e63ya Parampar\u0101 continue to inspire "
        "and shape this humble effort."
        "</div></div>",
        unsafe_allow_html=True
    )
    st.markdown("<small style='color:#444'>🕉️ vedantadhara.com</small>",
                unsafe_allow_html=True)


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="hero">'
    f'{om_tag}'
    f'<h1>Wisdom <span class="accent">Distiller</span></h1>'
    f'<div style="font-family:Cormorant Garamond,serif; font-style:italic;'
    f' font-size:1.05rem; color:#c9a96e; letter-spacing:1px; margin:0.3rem 0 0.1rem;">'
    f'\u015arava\u1e47a &middot; Manana &middot; Nididhy\u0101sana</div>'
    f'<div style="font-size:0.82rem; color:#aaa; letter-spacing:0.8px; margin-bottom:0.2rem;">'
    f'<div style="font-size:0.82rem; color:#aaa; letter-spacing:0.8px; margin-bottom:0.2rem;">'
    'श्रवण · मनन · निदिध्यासन</div>'
    f'<div style="font-size:0.78rem; color:#999; font-style:italic; letter-spacing:0.5px;">'
    f'Listening &middot; Reflection &middot; Contemplation</div>'
    f'<p class="subtitle" style="margin-top:0.6rem;">'
    f'Transcribe &middot; Translate &middot; Summarize &middot; Export &middot; Audio &middot; Video &middot; Documents</p>'
    f'</div>',
    unsafe_allow_html=True
)

# ── Tagline — centered ─────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center; padding:1.5rem 2rem 1rem; max-width:700px; margin:0 auto;'>"
    "<div style='font-family:Cormorant Garamond,serif; font-size:1.6rem; font-weight:600;"
    " line-height:1.4; color:#f0e8d8; margin-bottom:1rem;'>"
    "Distill the wisdom of sacred discourses into<br/>"
    "<span style='color:#c9a96e;'>clear, lasting insights.</span>"
    "</div>"
    "<div style='font-size:0.95rem; color:#aaa; line-height:1.85; margin:0 auto 1.2rem;'>"
    "Upload your spiritual discourses \u2014 in audio or video \u2014 and receive a beautifully "
    "structured transcript, summary, and table of key teachings, with Sanskrit terms "
    "transliterated into English. Output available in "
    "<b style='color:#b8a88a;'>English (default)</b>, "
    "<b style='color:#b8a88a;'>Hindi</b>, "
    "<b style='color:#b8a88a;'>Kannada</b>, "
    "<b style='color:#b8a88a;'>Telugu</b>, "
    "<b style='color:#b8a88a;'>Tamil</b>, "
    "<b style='color:#b8a88a;'>Marathi</b>, and "
    "<b style='color:#b8a88a;'>Gujarati</b>."
    "</div>"
    "<div style='display:flex; gap:1.2rem; flex-wrap:wrap;"
    " align-items:center; justify-content:center;'>"
    "<span style='color:#c9a96e;'>\u2756</span>"
    "<span style='font-size:0.82rem; color:#999;'>AI-Powered Transcription</span>"
    "<span style='color:#c9a96e;'>\u2756</span>"
    "<span style='font-size:0.82rem; color:#999;'>Sanskrit Transliteration</span>"
    "<span style='color:#c9a96e;'>\u2756</span>"
    "<span style='font-size:0.82rem; color:#999;'>Export as PDF or Word</span>"
    "<span style='color:#c9a96e;'>\u2756</span>"
    "<span style='font-size:0.82rem; color:#999;'>7 Language Outputs</span>"
    "</div></div>",
    unsafe_allow_html=True
)

# ── Bring-your-own-keys notice ────────────────────────────────────────────────
st.markdown(
    "<div style='max-width:700px; margin:0 auto 1rem; background:#111;"
    " border:1px solid #2a2a2a; border-left:3px solid #c9a96e; border-radius:12px;"
    " padding:1.1rem 1.5rem; text-align:center;'>"
    "<div style='font-size:0.9rem; color:#c9a96e; font-weight:600; margin-bottom:0.4rem;'>"
    "🔑 Before you begin — this app runs on your own API keys</div>"
    "<div style='font-size:0.82rem; color:#999; line-height:1.8;'>"
    "Wisdom Distiller is offered freely as seva, but the AI services it uses "
    "(Anthropic Claude for summarization, OpenAI Whisper for transcription) "
    "require your personal API keys. Setup takes only a few minutes and costs "
    "just a few cents per discourse. "
    "Open the <b style='color:#b8a88a;'>sidebar on the left</b> for step-by-step "
    "instructions to create both keys. Your keys are never stored."
    "</div></div>",
    unsafe_allow_html=True
)

# ── About box ──────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='about-box'>"
    "<b>Welcome to Wisdom Distiller</b> \u2014 an AI-powered platform for transcribing and "
    "summarizing spiritual discourses, lectures, and educational content. "
    "Upload <b>audio files</b> (MP3, WAV, M4A) or <b>video files</b> (MP4) \u2014 "
    "get back a clean transcript, structured summary, or a beautifully formatted table "
    "of key insights, with Sanskrit terms transliterated into English. "
    "Output available in <b>English</b>, <b>Hindi</b>, <b>Kannada</b>, "
    "<b>Telugu</b>, <b>Tamil</b>, <b>Marathi</b>, and <b>Gujarati</b>. Click any tool below to get started."
    "</div>",
    unsafe_allow_html=True
)

# ── Navigation cards ───────────────────────────────────────────────────────────
st.markdown("## Choose a Tool")

def nav_card(col, icon, title, desc, btn_label, btn_key, page_path):
    with col:
        st.markdown(
            f"<div style='background:#111; border:1px solid #2a2a2a;"
            f"border-top:3px solid #c9a96e; border-radius:12px; padding:1.2rem;"
            f"text-align:center; min-height:140px;'>"
            f"<div style='font-size:1.8rem; margin-bottom:0.4rem;'>{icon}</div>"
            f"<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem;"
            f"color:#e8e0d4; margin-bottom:0.4rem;'>{title}</div>"
            f"<div style='font-size:0.76rem; color:#888;'>{desc}</div>"
            f"</div>",
            unsafe_allow_html=True
        )
        if st.button(btn_label, key=btn_key):
            st.switch_page(page_path)

# ── Row 1: Transcription tools ────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
nav_card(col1, "🎙️", "Audio Summarizer",
         "Upload 1–5 MP3/WAV/M4A files",
         "🎙️ Open Audio Summarizer", "btn_audio",
         "pages/2_Audio_Summarizer.py")
nav_card(col2, "📜", "Discourse Transcriber",
         "Full structured transcript with sections",
         "📜 Open Transcriber", "btn_transcriber",
         "pages/3_Discourse_Transcriber.py")
nav_card(col3, "🎬", "Video Summarizer",
         "YouTube URL or MP4 upload",
         "🎬 Open Video Summarizer", "btn_video",
         "pages/4_Video_Summarizer.py")

st.markdown("<br/>", unsafe_allow_html=True)

# ── Row 2 ─────────────────────────────────────────────────────────────────────
col4, col5, col6 = st.columns(3)
nav_card(col4, "📄", "Document Combiner",
         "Merge multiple transcripts",
         "📄 Open Document Combiner", "btn_doc",
         "pages/5_Document_Combiner.py")
nav_card(col5, "💎", "Wisdom Extractor",
         "Verbatim quotes · YouTube · Reels",
         "💎 Open Wisdom Extractor", "btn_wisdom",
         "pages/6_Wisdom_Extractor.py")
nav_card(col6, "🪷", "Manana & Nididhyāsana Toolkit",
         "Questions · Essence card · Revision plan · Flashcards",
         "🪷 Open Toolkit", "btn_manana",
         "pages/7_Manana_Toolkit.py")

st.markdown("<br/>", unsafe_allow_html=True)

# ── Row 3 ─────────────────────────────────────────────────────────────────────
col7, col8, col9 = st.columns(3)
nav_card(col7, "🕉️", "About the App",
         "What makes Wisdom Distiller unique",
         "🕉️ Open About", "btn_about",
         "pages/8_About_the_App.py")
nav_card(col8, "❓", "FAQ",
         "Help · Getting started · Troubleshooting",
         "❓ Open FAQ", "btn_faq",
         "pages/9_FAQ.py")
nav_card(col9, "🌟", "Feedback & Reviews",
         "Share your experience · Read what others say",
         "🌟 Share Feedback", "btn_feedback",
         "pages/12_Feedback.py")

st.markdown(
    "<div style='text-align:center; margin-top:0.5rem;'>"
    "<small style='color:#444;'>Or use the sidebar navigation to open each tool.</small>"
    "</div>",
    unsafe_allow_html=True
)

# ── Persistent visitor counter via Google Sheets ─────────────────────────────
def _get_gsheet():
    """Return connected Google Sheet or None."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        scopes = ["https://www.googleapis.com/auth/spreadsheets",
                  "https://www.googleapis.com/auth/drive"]
        creds  = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client.open_by_key(st.secrets["FEEDBACK_SHEET_ID"])
    except Exception:
        return None

def _get_device_type():
    """Detect mobile vs desktop from user agent."""
    try:
        ua = st.context.headers.get("user-agent", "").lower()
        if any(m in ua for m in ["iphone","android","mobile","ipad"]):
            return "Mobile"
        return "Desktop"
    except Exception:
        return "Unknown"

def _get_country():
    """Get visitor country via free IP geolocation API (country only, no personal data)."""
    try:
        import urllib.request, json
        with urllib.request.urlopen("https://ipapi.co/json/", timeout=3) as r:
            data = json.loads(r.read())
        return data.get("country_name", "Unknown")
    except Exception:
        return "Unknown"

def _log_visit(sheet, device, country):
    """Log this visit to VisitorLog tab and update summary counter."""
    from datetime import datetime
    try:
        # ── Summary counter (Visitors tab) ────────────────────────────────
        try:
            vs = sheet.worksheet("Visitors")
        except Exception:
            vs = sheet.add_worksheet("Visitors", rows=10, cols=2)
            vs.append_row(["Total Visits", "Sessions"])
            vs.append_row([0, 0])
        row    = vs.row_values(2)
        visits = int(row[0]) if row and row[0] else 0
        vs.update("A2", [[visits + 1, visits + 1]])

        # ── Detailed log (VisitorLog tab) ──────────────────────────────────
        try:
            vl = sheet.worksheet("VisitorLog")
        except Exception:
            vl = sheet.add_worksheet("VisitorLog", rows=5000, cols=5)
            vl.append_row(["Timestamp", "Device", "Country", "Day", "Hour"])

        now = datetime.now()
        vl.append_row([
            now.strftime("%Y-%m-%d %H:%M"),
            device,
            country,
            now.strftime("%A"),          # e.g. Monday
            now.strftime("%H:00"),        # e.g. 14:00
        ])
        return visits + 1
    except Exception:
        return None

try:
    if "page_visit_counted" not in st.session_state:
        st.session_state["page_visit_counted"] = True

        # Collect analytics (runs once per session)
        device  = _get_device_type()
        country = _get_country()
        st.session_state["_device"]  = device
        st.session_state["_country"] = country

        sheet = _get_gsheet()
        if sheet:
            total_visits = _log_visit(sheet, device, country)
            total_visits = total_visits if total_visits else "—"
        else:
            total_visits = "—"

        st.session_state["_total_visits"] = total_visits
    else:
        total_visits = st.session_state.get("_total_visits", "—")

    st.markdown(
        "<div style='text-align:center; padding:1rem 0 0.5rem;'>"
        "<div style='display:inline-flex; gap:2rem; background:#111; border:1px solid #1e1e1e;"
        " border-radius:10px; padding:0.6rem 2rem;'>"
        f"<div style='text-align:center;'>"
        f"<div style='font-family:Cormorant Garamond,serif; font-size:1.4rem;"
        f" color:#c9a96e; font-weight:600;'>{total_visits}</div>"
        f"<div style='font-size:0.7rem; color:#555; text-transform:uppercase;"
        f" letter-spacing:0.5px;'>Total Visits</div></div>"
        "</div></div>",
        unsafe_allow_html=True
    )
except Exception:
    pass

# ── Gurudev photo + Quote — at the BOTTOM ─────────────────────────────────────
st.markdown("<hr style='border-color:#1e1e1e; margin:2rem 0 1.5rem;'/>",
            unsafe_allow_html=True)

st.markdown(
    "<div style='text-align:center; padding:1rem 1rem 2rem;'>"
    + gurudev_img
    + "<div style='font-size:0.72rem; color:#7a5c44; margin-top:8px; font-style:italic;'>"
    "P\u016bjya Sw\u0101m\u012b Chinmay\u0101nanda</div>"
    "<div style='font-family:Cormorant Garamond,serif; font-style:italic;"
    " font-size:1.1rem; color:#c9a96e; line-height:1.9; margin:1rem auto 0;"
    " max-width:500px;'>"
    "\u201cRenounce your ego\u201d is the Lord\u2019s only request;<br/>"
    "\u201cAnd I will make you God\u201d is the promise."
    "</div>"
    "<div style='font-family:Cormorant Garamond,serif; font-size:1rem;"
    " color:#c9a96e; font-style:italic; margin-top:0.5rem;'>"
    "\u2014 <em>P\u016bjya Sw\u0101m\u012b Chinmay\u0101nanda</em>"
    "</div>"
    "<div style='font-size:0.72rem; color:#555; margin-top:0.2rem; font-style:italic;'>"
    "(P\u016bjya Sw\u0101m\u012b Chinmay\u0101nanda \u2014 the Bliss of Pure Consciousness)"
    "</div></div>",
    unsafe_allow_html=True
)
