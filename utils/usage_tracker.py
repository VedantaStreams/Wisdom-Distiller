"""
Usage tracker for Wisdom Distiller.
Tracks per-user usage using a combination of browser session ID
stored in Streamlit session state and a shared JSON file.
Each unique session gets 5 free uses before being prompted to add their own API keys.
"""
import json
import os
import uuid
import streamlit as st
from pathlib import Path

FREE_USES = 5


def _load_data() -> dict:
    """Load usage data from session state (filesystem is read-only on Streamlit Cloud)."""
    return st.session_state.get("_usage_data", {})


def _save_data(data: dict):
    """Save usage data to session state."""
    st.session_state["_usage_data"] = data


def get_user_id() -> str:
    """Get or create a unique ID for this browser session."""
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = str(uuid.uuid4())[:12]
    return st.session_state["user_id"]


def get_usage_count() -> int:
    """Get how many times this user has used the app."""
    user_id = get_user_id()
    data = _load_data()
    return data.get(user_id, 0)


def increment_usage():
    """Increment usage count for this user."""
    user_id = get_user_id()
    data = _load_data()
    data[user_id] = data.get(user_id, 0) + 1
    _save_data(data)


def uses_remaining() -> int:
    """How many free uses remain for this user."""
    return max(0, FREE_USES - get_usage_count())


def is_app_owner() -> bool:
    """Check if this is the app owner (using Streamlit Secrets directly).
    App owner always has unlimited access."""
    try:
        # Owner is identified by a special OWNER_KEY in secrets
        owner_key = st.secrets.get("OWNER_KEY", "")
        session_key = st.session_state.get("owner_key", "")
        if owner_key and session_key == owner_key:
            return True
        # Also grant unlimited if UNLIMITED_ACCESS secret is set to true
        if str(st.secrets.get("UNLIMITED_ACCESS", "")).lower() == "true":
            return True
    except Exception:
        pass
    return False


def has_own_keys() -> bool:
    """Check if user has provided their own API keys."""
    # App owner always gets unlimited
    if is_app_owner():
        return True
    ak = st.session_state.get("anthropic_key", "")
    ok = st.session_state.get("openai_key", "")
    try:
        shared_ak = st.secrets.get("ANTHROPIC_API_KEY", "")
        shared_ok = st.secrets.get("OPENAI_API_KEY", "")
        if ak == shared_ak and ok == shared_ok:
            return False
        if ak and ok and ak != shared_ak:
            return True
    except Exception:
        pass
    return False


def check_usage_limit() -> bool:
    """
    Check if user can proceed.
    Returns True if allowed, False if blocked.
    Shows appropriate message.
    """
    # If user has their own keys, always allow
    if has_own_keys():
        return True

    remaining = uses_remaining()

    if remaining <= 0:
        # Blocked — show message with API setup instructions
        st.error("🔒 You have used all 5 free sessions.")
        st.markdown("""
<div style="background:#111; border:1px solid #2a2a2a; border-left:3px solid #c9a96e;
            border-radius:10px; padding:1.2rem 1.5rem; margin-top:0.5rem;">
    <div style="font-family:'Cormorant Garamond',serif; font-size:1.05rem;
                color:#c9a96e; font-weight:600; margin-bottom:0.8rem;">
        🔑 Set Up Your Own API Keys to Continue
    </div>
    <div style="font-size:0.85rem; color:#888; line-height:1.9;">
        Both keys are <b style="color:#b8a88a;">free to create</b> and cost only a few cents per session.<br/><br/>
        <b style="color:#b8a88a;">Step 1 — OpenAI (Whisper transcription):</b><br/>
        Go to <a href="https://platform.openai.com/signup" target="_blank"
        style="color:#c9a96e;">platform.openai.com/signup</a>
        → API Keys → Create key → Add $5 credit<br/><br/>
        <b style="color:#b8a88a;">Step 2 — Anthropic (Claude summarization):</b><br/>
        Go to <a href="https://console.anthropic.com" target="_blank"
        style="color:#c9a96e;">console.anthropic.com</a>
        → API Keys → Create key → Add $5 credit<br/><br/>
        <b style="color:#b8a88a;">Step 3 — Enter both keys in the sidebar</b>
        on the left and you are all set!
    </div>
</div>
""", unsafe_allow_html=True)
        return False

    # Warn when getting close
    if remaining <= 2:
        st.warning(
            f"⚠️ You have **{remaining} free use(s)** remaining. "
            f"After that, please set up your own API keys — "
            f"see the **Get the App** page for instructions."
        )

    return True


def show_usage_badge():
    """Show a small usage counter badge."""
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
            f"<div style='font-size:0.75rem; color:{color}; text-align:right;'>"
            f"🔢 {remaining} free use(s) remaining</div>",
            unsafe_allow_html=True
        )

