"""
Usage tracker for Wisdom Distiller.
Uses Google login email for persistent cross-session tracking via Google Sheets.
After 5 uses, visitors are blocked until they enter their own API keys.
"""
import streamlit as st

FREE_USES = 5

# Emails that always have unlimited access (add more as needed)
UNLIMITED_EMAILS = [
    "vedantavani.manana@gmail.com",
]


def _get_usage_sheet():
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


def _get_user_email() -> str:
    """Get logged-in user email from Streamlit auth."""
    try:
        user = st.experimental_user
        if user and user.email:
            return user.email.lower().strip()
    except Exception:
        pass
    try:
        user = st.user
        if user and user.email:
            return user.email.lower().strip()
    except Exception:
        pass
    return ""


def _get_row(ws, email: str):
    """Find row for this email. Returns (row_index, use_count) or (None, 0)."""
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
    """Save updated count to sheet."""
    from datetime import datetime
    now     = datetime.now().strftime("%Y-%m-%d %H:%M")
    blocked = "YES" if count >= FREE_USES else "NO"
    try:
        if row_idx:
            ws.update("B" + str(row_idx), [[count]])
            ws.update("D" + str(row_idx), [[now]])
            ws.update("E" + str(row_idx), [[blocked]])
        else:
            first = datetime.now().strftime("%Y-%m-%d %H:%M")
            ws.append_row([email, count, first, now, blocked])
    except Exception:
        pass


def is_app_owner() -> bool:
    """App owner has unlimited access."""
    try:
        if str(st.secrets.get("UNLIMITED_ACCESS", "")).lower() == "true":
            return True
    except Exception:
        pass
    email = _get_user_email()
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


def get_usage_count() -> int:
    """Get usage count for this user's email."""
    if has_own_keys():
        return 0

    if "_usage_count_cache" in st.session_state:
        return st.session_state["_usage_count_cache"]

    email = _get_user_email()
    if not email:
        return st.session_state.get("_usage_fallback", 0)

    ws = _get_usage_sheet()
    if ws is None:
        return st.session_state.get("_usage_fallback", 0)

    _, count = _get_row(ws, email)
    st.session_state["_usage_count_cache"] = count
    return count


def increment_usage():
    """Increment usage count for this user."""
    if has_own_keys():
        return

    new_count = get_usage_count() + 1
    st.session_state["_usage_count_cache"] = new_count

    email = _get_user_email()
    if not email:
        st.session_state["_usage_fallback"] = new_count
        return

    ws = _get_usage_sheet()
    if ws is None:
        st.session_state["_usage_fallback"] = new_count
        return

    row_idx, _ = _get_row(ws, email)
    _save_row(ws, email, new_count, row_idx)


def uses_remaining() -> int:
    return max(0, FREE_USES - get_usage_count())


def check_usage_limit() -> bool:
    """Returns True if user can proceed, False if blocked."""
    if has_own_keys():
        return True

    remaining = uses_remaining()

    if remaining <= 0:
        email = _get_user_email()
        st.error("🔒 You have used all 5 free sessions, " + (email or "seeker") + ".")
        st.markdown("""
<div style="background:#111; border:1px solid #2a2a2a; border-left:3px solid #c9a96e;
            border-radius:10px; padding:1.4rem 1.8rem; margin-top:0.5rem;">
    <div style="font-family:'Cormorant Garamond',serif; font-size:1.1rem;
                color:#c9a96e; font-weight:600; margin-bottom:1rem;">
        Get Your Own API Keys to Continue — Free & Easy
    </div>
    <div style="font-size:0.88rem; color:#888; line-height:2;">
        Each session costs only a few cents with your own keys.
        A $5 credit on each platform lasts months of regular use.<br/><br/>
        <b style="color:#b8a88a;">Anthropic API Key (for summarization):</b><br/>
        Go to console.anthropic.com → API Keys → Create Key<br/><br/>
        <b style="color:#b8a88a;">OpenAI API Key (for audio transcription):</b><br/>
        Go to platform.openai.com/api-keys → Create key → Add $5 credit<br/><br/>
        <b style="color:#b8a88a;">Then enter both keys in the sidebar on the Home page.</b>
    </div>
</div>
""", unsafe_allow_html=True)
        return False

    if remaining <= 2:
        st.warning(
            "You have " + str(remaining) + " free use(s) remaining. "
            "Please set up your own API keys after that."
        )
    return True


def show_usage_badge():
    """Show usage badge in sidebar."""
    if has_own_keys():
        st.markdown(
            "<div style='font-size:0.75rem; color:#555; text-align:right;'>"
            "✅ Using your own API keys</div>",
            unsafe_allow_html=True
        )
    else:
        remaining = uses_remaining()
        color = "#c9a96e" if remaining > 2 else "#ff6b6b"
        st.markdown(
            "<div style='font-size:0.75rem; color:" + color + "; text-align:right;'>"
            "🔢 " + str(remaining) + " of 5 free uses remaining</div>",
            unsafe_allow_html=True
        )


def _get_ip() -> str:
    """Legacy function — now returns email for compatibility."""
    return _get_user_email() or "unknown"
