"""
Usage tracker for Wisdom Distiller.
- Home page always visible to everyone
- After 5 uses, user must enter their own API keys
- Usage tracked per browser session
"""
import streamlit as st

FREE_USES = 5


def is_app_owner() -> bool:
    try:
        if str(st.secrets.get("UNLIMITED_ACCESS", "")).lower() == "true":
            return True
    except Exception:
        pass
    return False


def has_own_keys() -> bool:
    """User has entered their own API keys."""
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


def _get_user_email() -> str:
    """Get logged in user email."""
    try:
        if st.user.is_logged_in:
            return (st.user.email or "").lower().strip()
    except Exception:
        pass
    return ""


def _get_sheet():
    """Connect to UsageTracker tab."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            pk = creds_dict["private_key"]
        creds_dict["private_key"] = pk.replace("\\n", "\n")
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


def _get_count_from_sheet(email: str) -> tuple:
    """Returns (row_idx, count)."""
    try:
        ws = _get_sheet()
        if ws is None:
            return None, 0
        cell = ws.find(email, in_column=1)
        if cell:
            row   = ws.row_values(cell.row)
            count = int(row[1]) if len(row) > 1 and row[1] else 0
            return cell.row, count
        return None, 0
    except Exception:
        return None, 0


def _save_count_to_sheet(email: str, count: int, row_idx=None):
    try:
        ws = _get_sheet()
        if ws is None:
            return
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        blocked = "YES" if count >= FREE_USES else "NO"
        if row_idx:
            ws.update("B" + str(row_idx), [[count]])
            ws.update("D" + str(row_idx), [[now]])
            ws.update("E" + str(row_idx), [[blocked]])
        else:
            ws.append_row([email, count, now, now, blocked])
    except Exception:
        pass


def get_usage_count() -> int:
    if has_own_keys():
        return 0
    if "_usage_cache" in st.session_state:
        return st.session_state["_usage_cache"]
    email = _get_user_email()
    if not email:
        return st.session_state.get("_usage_count", 0)
    _, count = _get_count_from_sheet(email)
    st.session_state["_usage_cache"] = count
    return count


def increment_usage():
    if has_own_keys():
        return
    new_count = get_usage_count() + 1
    st.session_state["_usage_cache"] = new_count
    email = _get_user_email()
    if not email:
        st.session_state["_usage_count"] = new_count
        return
    row_idx, _ = _get_count_from_sheet(email)
    _save_count_to_sheet(email, new_count, row_idx)


def uses_remaining() -> int:
    return max(0, FREE_USES - get_usage_count())


def check_usage_limit() -> bool:
    """
    Returns True if user can proceed.
    Returns False and shows block message after 5 uses.
    """
    if has_own_keys():
        return True

    remaining = uses_remaining()

    if remaining <= 0:
        st.markdown("""
<div style="background:#111; border:2px solid #c9a96e;
            border-radius:12px; padding:2rem; margin:1rem 0; text-align:center;">
    <div style="font-size:2rem; margin-bottom:0.5rem;">🔒</div>
    <div style="font-family:'Cormorant Garamond',serif; font-size:1.3rem;
                color:#c9a96e; font-weight:600; margin-bottom:1rem;">
        You have used all 5 free sessions
    </div>
    <div style="font-size:0.9rem; color:#888; line-height:2; margin-bottom:1.5rem;">
        To continue using Wisdom Distiller, please get your own API keys.<br/>
        This takes about 5 minutes and costs only a few cents per session.
    </div>
    <div style="text-align:left; background:#0d0d0d; border-radius:8px;
                padding:1.2rem 1.5rem; margin-bottom:1rem;">
        <div style="font-size:0.88rem; color:#b8a88a; font-weight:600;
                    margin-bottom:0.5rem;">
            Step 1 — Get Anthropic API Key (for summarization):
        </div>
        <div style="font-size:0.85rem; color:#777; line-height:1.9;">
            1. Go to <a href="https://console.anthropic.com" target="_blank"
            style="color:#c9a96e;">console.anthropic.com</a><br/>
            2. Sign up → click API Keys → Create Key<br/>
            3. Copy the key (starts with sk-ant-)
        </div>
    </div>
    <div style="text-align:left; background:#0d0d0d; border-radius:8px;
                padding:1.2rem 1.5rem; margin-bottom:1rem;">
        <div style="font-size:0.88rem; color:#b8a88a; font-weight:600;
                    margin-bottom:0.5rem;">
            Step 2 — Get OpenAI API Key (for audio transcription):
        </div>
        <div style="font-size:0.85rem; color:#777; line-height:1.9;">
            1. Go to <a href="https://platform.openai.com/api-keys" target="_blank"
            style="color:#c9a96e;">platform.openai.com/api-keys</a><br/>
            2. Sign up → Create new secret key<br/>
            3. Add $5 credit under Billing → copy the key
        </div>
    </div>
    <div style="text-align:left; background:#0d0d0d; border-radius:8px;
                padding:1.2rem 1.5rem;">
        <div style="font-size:0.88rem; color:#b8a88a; font-weight:600;
                    margin-bottom:0.5rem;">
            Step 3 — Enter both keys in the sidebar on the Home page
        </div>
        <div style="font-size:0.85rem; color:#777; line-height:1.9;">
            Once entered, you have <b style="color:#c9a96e;">unlimited access</b>
            with no restrictions. A $5 credit typically lasts several months
            of regular use.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
        return False

    if remaining == 1:
        st.warning(
            "⚠️ This is your **last free session**. "
            "Please get your own API keys to continue after this — "
            "see the Home page sidebar for instructions."
        )
    elif remaining == 2:
        st.warning(
            "⚠️ You have **" + str(remaining) + " free sessions** remaining. "
            "Please get your own API keys to continue after that."
        )
    return True


def show_usage_badge():
    if has_own_keys():
        st.markdown(
            "<div style='font-size:0.75rem;color:#555;text-align:right;'>"
            "✅ Using your own API keys — unlimited access</div>",
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
