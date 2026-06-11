"""
Usage tracker for Wisdom Distiller.
Tracks usage by Google login email via Google Sheets.
5 free uses per user, then they must enter their own API keys.
"""
import streamlit as st

FREE_USES = 5
UNLIMITED_EMAILS = [
    "vedantavani.manana@gmail.com",
    "sumarajashankar@gmail.com",
]


def get_logged_in_email() -> str:
    """Get email of logged in user. Empty string if not logged in."""
    try:
        if st.experimental_user.is_logged_in:
            return (st.experimental_user.email or "").lower().strip()
    except Exception:
        pass
    return ""


def is_logged_in() -> bool:
    """Check if user is logged in via Google."""
    try:
        return bool(st.experimental_user.is_logged_in)
    except Exception:
        return False


def is_app_owner() -> bool:
    """App owner has unlimited access."""
    try:
        if str(st.secrets.get("UNLIMITED_ACCESS", "")).lower() == "true":
            return True
    except Exception:
        pass
    email = get_logged_in_email()
    if email and email in UNLIMITED_EMAILS:
        return True
    return False


def has_own_keys() -> bool:
    """User entered their own API keys."""
    if is_app_owner():
        return True
    try:
        ak = st.session_state.get("anthropic_key", "")
        ok = st.session_state.get("openai_key", "")
        shared_ak = st.secrets.get("ANTHROPIC_API_KEY", "")
        shared_ok = st.secrets.get("OPENAI_API_KEY", "")
        if ak and ok and ak != shared_ak and ok != shared_ok:
            return True
    except Exception:
        pass
    return False


def _get_sheet():
    """Connect to UsageTracker tab in Google Sheet."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds  = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet  = client.open_by_key(st.secrets["FEEDBACK_SHEET_ID"])
        try:
            ws = sheet.worksheet("UsageTracker")
        except Exception:
            ws = sheet.add_worksheet("UsageTracker", rows=10000, cols=5)
            ws.append_row(["Email", "UseCount", "FirstSeen", "LastSeen", "Blocked"])
        return ws
    except Exception:
        return None


def _get_row(ws, email: str):
    """Find row for this email."""
    try:
        cell = ws.find(email, in_column=1)
        if cell:
            row   = ws.row_values(cell.row)
            count = int(row[1]) if len(row) > 1 and row[1] else 0
            return cell.row, count
    except Exception:
        pass
    return None, 0


def _save_row(ws, email: str, count: int, row_idx=None):
    """Save usage to sheet."""
    from datetime import datetime
    now     = datetime.now().strftime("%Y-%m-%d %H:%M")
    blocked = "YES" if count >= FREE_USES else "NO"
    try:
        if row_idx:
            ws.update("B" + str(row_idx), [[count]])
            ws.update("D" + str(row_idx), [[now]])
            ws.update("E" + str(row_idx), [[blocked]])
        else:
            ws.append_row([email, count, now, now, blocked])
    except Exception:
        pass


def get_usage_count() -> int:
    """Get usage count for logged in user."""
    if has_own_keys():
        return 0
    if "_usage_cache" in st.session_state:
        return st.session_state["_usage_cache"]
    email = get_logged_in_email()
    if not email:
        return 0
    ws = _get_sheet()
    if ws is None:
        return 0
    _, count = _get_row(ws, email)
    st.session_state["_usage_cache"] = count
    return count


def increment_usage():
    """Increment usage for logged in user."""
    if has_own_keys():
        return
    email = get_logged_in_email()
    if not email:
        return
    new_count = get_usage_count() + 1
    st.session_state["_usage_cache"] = new_count
    ws = _get_sheet()
    if ws is None:
        return
    row_idx, _ = _get_row(ws, email)
    _save_row(ws, email, new_count, row_idx)


def uses_remaining() -> int:
    return max(0, FREE_USES - get_usage_count())


def check_usage_limit() -> bool:
    """Returns True if user can proceed."""
    if has_own_keys():
        return True
    remaining = uses_remaining()
    if remaining <= 0:
        email = get_logged_in_email()
        st.error("🔒 You have used all 5 free sessions.")
        st.markdown("""
<div style="background:#111; border:1px solid #2a2a2a; border-left:3px solid #c9a96e;
            border-radius:10px; padding:1.4rem 1.8rem; margin-top:0.5rem;">
    <div style="font-family:'Cormorant Garamond',serif; font-size:1.1rem;
                color:#c9a96e; font-weight:600; margin-bottom:1rem;">
        🔑 Get Your Own API Keys to Continue
    </div>
    <div style="font-size:0.88rem; color:#888; line-height:2;">
        Each session costs only a few cents. A $5 credit lasts months.<br/><br/>
        <b style="color:#b8a88a;">Step 1 — Anthropic API Key:</b><br/>
        Go to <a href="https://console.anthropic.com" target="_blank"
        style="color:#c9a96e;">console.anthropic.com</a>
        → API Keys → Create Key → copy it<br/><br/>
        <b style="color:#b8a88a;">Step 2 — OpenAI API Key:</b><br/>
        Go to <a href="https://platform.openai.com/api-keys" target="_blank"
        style="color:#c9a96e;">platform.openai.com/api-keys</a>
        → Create key → Add $5 credit<br/><br/>
        <b style="color:#b8a88a;">Step 3 — Enter both keys in the sidebar on the Home page.</b>
    </div>
</div>
""", unsafe_allow_html=True)
        return False
    if remaining <= 2:
        st.warning(
            "⚠️ You have **" + str(remaining) + " free use(s)** remaining. "
            "Please set up your own API keys after that."
        )
    return True


def show_usage_badge():
    if has_own_keys():
        st.markdown(
            "<div style='font-size:0.75rem;color:#555;text-align:right;'>"
            "✅ Using your own API keys</div>",
            unsafe_allow_html=True
        )
    else:
        remaining = uses_remaining()
        color = "#c9a96e" if remaining > 2 else "#ff6b6b"
        st.markdown(
            "<div style='font-size:0.75rem;color:" + color + ";text-align:right;'>"
            "🔢 " + str(remaining) + " of 5 free uses remaining</div>",
            unsafe_allow_html=True
        )
