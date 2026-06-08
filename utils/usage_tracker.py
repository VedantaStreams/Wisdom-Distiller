"""
Usage tracker for Wisdom Distiller.
Uses IP address + Google Sheets for persistent cross-session tracking.
After 5 uses, visitors are blocked until they enter their own API keys.
"""
import streamlit as st

FREE_USES = 5


def _get_ip() -> str:
    """
    Get visitor's real public IP by calling ipify.org from the SERVER side.
    On Streamlit Cloud, each user gets a unique server-side connection,
    and ipify returns the real client IP via Streamlit's proxy headers.
    Falls back to browser fingerprint if unavailable.
    """
    # Cache in session to avoid repeated calls
    if "_cached_ip" in st.session_state:
        return st.session_state["_cached_ip"]

    # Method 1: ipify API — most reliable way to get real public IP
    # Streamlit Cloud passes the real client IP to outbound requests
    try:
        import urllib.request, json
        req = urllib.request.Request(
            "https://api64.ipify.org?format=json",
            headers={"User-Agent": "WisdomDistiller/1.0"}
        )
        with urllib.request.urlopen(req, timeout=4) as r:
            data = json.loads(r.read())
            ip = data.get("ip", "")
            if ip and not ip.startswith(
                ("10.", "172.1", "172.2", "172.3",
                 "192.168.", "127.", "::1")
            ):
                st.session_state["_cached_ip"] = ip
                return ip
    except Exception:
        pass

    # Method 2: Browser fingerprint — stable within a browser profile
    # Uses user-agent + language — no random salt so it persists across sessions
    try:
        import hashlib
        headers = st.context.headers
        ua   = headers.get("user-agent", "unknown-ua")
        lang = headers.get("accept-language", "unknown-lang")
        # NO random salt — fingerprint is stable for same browser/device
        fingerprint = hashlib.sha256(
            (ua + lang).encode()
        ).hexdigest()[:20]
        result = "fp_" + fingerprint
        st.session_state["_cached_ip"] = result
        return result
    except Exception:
        pass

    # Method 3: Session UUID (last resort)
    try:
        import uuid
        if "_session_uid" not in st.session_state:
            st.session_state["_session_uid"] = "sid_" + str(uuid.uuid4())[:12]
        return st.session_state["_session_uid"]
    except Exception:
        pass

    return "unknown"


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
            ws.append_row(["IP", "UseCount", "FirstSeen", "LastSeen", "Blocked"])
        return ws
    except Exception:
        return None


def _get_row(ws, ip: str):
    """Find row for this IP. Returns (row_index, use_count) or (None, 0)."""
    try:
        cell = ws.find(ip, in_column=1)
        if cell:
            row   = ws.row_values(cell.row)
            count = int(row[1]) if len(row) > 1 and row[1] else 0
            return cell.row, count
    except Exception:
        pass
    return None, 0


def _save_row(ws, ip: str, count: int, row_idx=None):
    """Save updated count to sheet."""
    from datetime import datetime
    now     = datetime.now().strftime("%Y-%m-%d %H:%M")
    blocked = "YES" if count >= FREE_USES else "NO"
    try:
        if row_idx:
            ws.update(f"B{row_idx}", [[count]])
            ws.update(f"D{row_idx}", [[now]])
            ws.update(f"E{row_idx}", [[blocked]])
        else:
            first = datetime.now().strftime("%Y-%m-%d %H:%M")
            ws.append_row([ip, count, first, now, blocked])
    except Exception:
        pass


# ── Public API ────────────────────────────────────────────────────────────────

def is_app_owner() -> bool:
    """App owner always has unlimited access."""
    try:
        if str(st.secrets.get("UNLIMITED_ACCESS", "")).lower() == "true":
            return True
    except Exception:
        pass
    return False


def has_own_keys() -> bool:
    """User entered their own API keys different from the shared ones."""
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
    """Get usage count for this visitor's IP from Google Sheets."""
    if has_own_keys():
        return 0

    # Cache in session to avoid repeated sheet reads
    if "_ip_usage_cache" in st.session_state:
        return st.session_state["_ip_usage_cache"]

    ip = _get_ip()
    if ip == "unknown":
        # Can't track — use session fallback
        count = st.session_state.get("_usage_fallback", 0)
        st.session_state["_ip_usage_cache"] = count
        return count

    ws = _get_usage_sheet()
    if ws is None:
        count = st.session_state.get("_usage_fallback", 0)
        st.session_state["_ip_usage_cache"] = count
        return count

    _, count = _get_row(ws, ip)
    st.session_state["_ip_usage_cache"] = count
    return count


def increment_usage():
    """Increment usage count for this visitor's IP."""
    if has_own_keys():
        return

    ip = _get_ip()
    new_count = get_usage_count() + 1
    st.session_state["_ip_usage_cache"] = new_count

    if ip == "unknown":
        st.session_state["_usage_fallback"] = new_count
        return

    ws = _get_usage_sheet()
    if ws is None:
        st.session_state["_usage_fallback"] = new_count
        return

    row_idx, _ = _get_row(ws, ip)
    _save_row(ws, ip, new_count, row_idx)


def uses_remaining() -> int:
    return max(0, FREE_USES - get_usage_count())


def check_usage_limit() -> bool:
    """
    Returns True if user can proceed.
    Returns False and shows block message if limit reached.
    """
    if has_own_keys():
        return True

    remaining = uses_remaining()

    if remaining <= 0:
        st.error("🔒 You have used all 5 free sessions.")
        st.markdown("""
<div style="background:#111; border:1px solid #2a2a2a; border-left:3px solid #c9a96e;
            border-radius:10px; padding:1.4rem 1.8rem; margin-top:0.5rem;">
    <div style="font-family:'Cormorant Garamond',serif; font-size:1.1rem;
                color:#c9a96e; font-weight:600; margin-bottom:1rem;">
        🔑 Get Your Own API Keys to Continue — It's Easy & Almost Free
    </div>
    <div style="font-size:0.88rem; color:#888; line-height:2;">
        Each session costs you only a few cents with your own keys.
        A $5 credit on each platform lasts for months of regular use.<br/><br/>
        <b style="color:#b8a88a;">Step 1 — Anthropic API Key (for summarization):</b><br/>
        1. Go to
        <a href="https://console.anthropic.com" target="_blank"
        style="color:#c9a96e;">console.anthropic.com</a><br/>
        2. Sign up → click <b>API Keys</b> → <b>Create Key</b><br/>
        3. Copy the key (starts with <code>sk-ant-</code>)<br/><br/>
        <b style="color:#b8a88a;">Step 2 — OpenAI API Key (for audio transcription):</b><br/>
        1. Go to
        <a href="https://platform.openai.com/api-keys" target="_blank"
        style="color:#c9a96e;">platform.openai.com/api-keys</a><br/>
        2. Sign up → click <b>Create new secret key</b><br/>
        3. Add a small credit ($5) under Billing<br/>
        4. Copy the key (starts with <code>sk-</code>)<br/><br/>
        <b style="color:#b8a88a;">Step 3 — Enter both keys in the sidebar on the Home page</b><br/>
        Once entered, you have unlimited access with no restrictions.
    </div>
</div>
""", unsafe_allow_html=True)
        return False

    if remaining <= 2:
        st.warning(
            f"⚠️ You have **{remaining} free use(s)** remaining. "
            f"Please set up your own API keys to continue after that — "
            f"it takes 5 minutes and costs only a few cents per session."
        )
    return True


def show_usage_badge():
    """Show usage badge in sidebar."""
    if has_own_keys():
        st.markdown(
            "<div style='font-size:0.75rem; color:#555; text-align:right;'>"
            "✅ Using your own API keys — unlimited access</div>",
            unsafe_allow_html=True
        )
    else:
        remaining = uses_remaining()
        color = "#c9a96e" if remaining > 2 else "#ff6b6b"
        st.markdown(
            f"<div style='font-size:0.75rem; color:{color}; text-align:right;'>"
