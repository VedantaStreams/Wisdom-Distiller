import streamlit as st
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.styles import SHARED_CSS

st.set_page_config(
    page_title="Get the App · Wisdom Distiller",
    page_icon="📱",
    layout="centered"
)
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── Home button in sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.page_link("app.py", label="🏠 Home")
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>", unsafe_allow_html=True)



# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>📱 Get the <span class="accent">App</span></h1>
    <p class="subtitle">Use the Wisdom Distiller on your iPhone, Android, or Desktop</p>
</div>
""", unsafe_allow_html=True)


# ── Usage Policy Banner ────────────────────────────────────────────────────────
st.markdown(
    "<div style='background:#1a1200; border:1px solid #c9a96e; border-radius:12px;"
    " padding:1.2rem 1.6rem; margin-bottom:1.5rem;'>"
    "<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem;"
    " color:#c9a96e; font-weight:600; margin-bottom:0.6rem;'>"
    "&#x1F4CB; Usage Policy</div>"
    "<div style='font-size:0.84rem; color:#aaa; line-height:1.85;'>"
    "This app is offered as a <b style='color:#b8a88a;'>free resource</b> for students, "
    "and fellow Vedantins. Anyone may use the app up to "
    "<b style='color:#c9a96e;'>5 times</b> using the shared access provided.<br/><br/>"
    "After 5 uses, you are kindly requested to <b style='color:#b8a88a;'>set up your own "
    "API keys</b> — both are free to start and cost only a few cents per session. "
    "Full setup instructions are in the <b style='color:#b8a88a;'>API Setup</b> tab below."
    "</div></div>",
    unsafe_allow_html=True
)


# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_iphone, tab_android, tab_api, tab_pricing, tab_feedback, tab_share = st.tabs([
    "🍎 iPhone",
    "🤖 Android",
    "🔑 API Setup (After 5 Uses)",
    "💰 Pricing",
    "📝 Feedback",
    "🔗 Share with Others"
])


# ══════════════════════════════════════════════════════════════════════════════
# IPHONE TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_iphone:

    st.markdown(
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.15rem;"
        " color:#c9a96e; font-weight:600; margin:1rem 0 0.6rem;'>"
        "Add to iPhone Home Screen</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:12px;"
        " padding:1.4rem 1.8rem; margin-bottom:1rem;'>"
        "<div style='font-size:0.84rem; color:#888; line-height:2.1;'>"
        "<b style='color:#b8a88a;'>1.</b> Open <b>Safari</b> on your iPhone<br/>"
        "<b style='color:#b8a88a;'>2.</b> Visit your app URL (e.g. <span style='color:#c9a96e;'>vedantadhara.streamlit.app</span>)<br/>"
        "<b style='color:#b8a88a;'>3.</b> Tap the <b>Share button</b> "
        "(square with arrow, bottom of screen)<br/>"
        "<b style='color:#b8a88a;'>4.</b> Scroll and tap <b>Add to Home Screen</b><br/>"
        "<b style='color:#b8a88a;'>5.</b> Tap <b>Add</b> — icon appears on home screen!"
        "</div></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a;"
        " border-left:3px solid #c9a96e; border-radius:8px;"
        " padding:0.8rem 1.2rem; margin-bottom:1.2rem;'>"
        "<div style='font-size:0.82rem; color:#888; line-height:1.85;'>"
        "&#x2705; No App Store download needed<br/>"
        "&#x2705; Looks and feels like a native app<br/>"
        "&#x2705; Free to use (first 5 sessions)<br/>"
        "&#x2705; Always up to date automatically<br/>"
        "&#x2705; Works on iPhone and iPad"
        "</div></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem;"
        " color:#c9a96e; font-weight:600; margin:1rem 0 0.4rem;'>"
        "Native iPhone App — Coming Soon</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:10px;"
        " padding:1.1rem 1.4rem;'>"
        "<div style='font-size:0.83rem; color:#888; line-height:1.8;'>"
        "A dedicated native iPhone app (built with Flutter) is planned for the "
        "App Store with features like direct audio recording and Voice Memos import.<br/><br/>"
        "To be notified at launch, email "
        "<a href='mailto:vedantavani.manana@gmail.com' style='color:#c9a96e;'>"
        "vedantavani.manana@gmail.com</a> with subject: <i>iPhone App Notification</i>"
        "</div></div>",
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# ANDROID TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_android:

    st.markdown(
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.15rem;"
        " color:#c9a96e; font-weight:600; margin:1rem 0 0.6rem;'>"
        "Add to Android Home Screen</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:12px;"
        " padding:1.4rem 1.8rem; margin-bottom:1rem;'>"
        "<div style='font-size:0.84rem; color:#888; line-height:2.1;'>"
        "<b style='color:#b8a88a;'>1.</b> Open <b>Chrome</b> on your Android phone<br/>"
        "<b style='color:#b8a88a;'>2.</b> Visit your app URL (e.g. <span style='color:#c9a96e;'>vedantadhara.streamlit.app</span>)<br/>"
        "<b style='color:#b8a88a;'>3.</b> Tap the <b>three dots menu</b> (top right)<br/>"
        "<b style='color:#b8a88a;'>4.</b> Tap <b>Add to Home screen</b><br/>"
        "<b style='color:#b8a88a;'>5.</b> Tap <b>Add</b> — icon appears on home screen!"
        "</div></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a;"
        " border-left:3px solid #c9a96e; border-radius:8px;"
        " padding:0.8rem 1.2rem; margin-bottom:1.2rem;'>"
        "<div style='font-size:0.82rem; color:#888; line-height:1.85;'>"
        "&#x2705; No Play Store download needed<br/>"
        "&#x2705; Works on all Android phones and tablets<br/>"
        "&#x2705; Free to use (first 5 sessions)<br/>"
        "&#x2705; Always up to date automatically<br/>"
        "&#x2705; Works on Chrome and Samsung Internet"
        "</div></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem;"
        " color:#c9a96e; font-weight:600; margin:1rem 0 0.4rem;'>"
        "Native Android App — Coming Soon</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:10px;"
        " padding:1.1rem 1.4rem;'>"
        "<div style='font-size:0.83rem; color:#888; line-height:1.8;'>"
        "A dedicated native Android app (built with Flutter) is planned for the "
        "Google Play Store with features like direct audio recording and file manager import.<br/><br/>"
        "To be notified at launch, email "
        "<a href='mailto:vedantavani.manana@gmail.com' style='color:#c9a96e;'>"
        "vedantavani.manana@gmail.com</a> with subject: <i>Android App Notification</i>"
        "</div></div>",
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# API SETUP TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_api:

    st.markdown(
        "<div class='about-box'>"
        "After your first <b>5 free uses</b>, you will need your own API keys to continue. "
        "Both keys are <b>free to set up</b> and cost only a few cents per session. "
        "Follow the steps below for each key."
        "</div>",
        unsafe_allow_html=True
    )

    # Cost table
    st.markdown(
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem;"
        " color:#c9a96e; font-weight:600; margin:0.5rem 0 0.6rem;'>"
        "What Does It Cost?</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:10px;"
        " padding:1.1rem 1.4rem; margin-bottom:1.2rem;'>"
        "<div style='font-size:0.83rem; color:#888; line-height:1.9;'>"
        "<b style='color:#b8a88a;'>OpenAI (Whisper transcription)</b><br/>"
        "&#x2022; Free credits when you sign up<br/>"
        "&#x2022; ~$0.006 per minute of audio after that<br/>"
        "&#x2022; A 20-min discourse costs about <b style='color:#c9a96e;'>$0.12</b><br/>"
        "&#x2022; A 1.5-hour discourse costs about <b style='color:#c9a96e;'>$0.54</b><br/><br/>"
        "<b style='color:#b8a88a;'>Anthropic (Claude summarization)</b><br/>"
        "&#x2022; Free credits when you sign up<br/>"
        "&#x2022; ~$0.01 to $0.05 per summary<br/>"
        "&#x2022; <b style='color:#c9a96e;'>$5 in credits = hundreds of summaries</b>"
        "</div></div>",
        unsafe_allow_html=True
    )

    # OpenAI setup
    st.markdown(
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem;"
        " color:#c9a96e; font-weight:600; margin:0.5rem 0 0.6rem;'>"
        "Step 1 — Get Your OpenAI API Key (Whisper)</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:12px;"
        " padding:1.4rem 1.8rem; margin-bottom:1rem;'>"
        "<div style='font-size:0.84rem; color:#888; line-height:2;'>"
        "<b style='color:#b8a88a;'>1.</b> Go to "
        "<a href='https://platform.openai.com/signup' target='_blank'"
        " style='color:#c9a96e;'>platform.openai.com/signup</a> "
        "and create a free account<br/>"
        "<b style='color:#b8a88a;'>2.</b> Once logged in, click your profile icon "
        "&#8594; <b>API Keys</b><br/>"
        "<b style='color:#b8a88a;'>3.</b> Click <b>Create new secret key</b><br/>"
        "<b style='color:#b8a88a;'>4.</b> Copy the key — it starts with <b>sk-</b><br/>"
        "<b style='color:#b8a88a;'>5.</b> Go to <b>Billing</b> &#8594; add $5 credit<br/>"
        "<b style='color:#b8a88a;'>6.</b> Paste the key in the sidebar of this app"
        "</div>"
        "<div style='margin-top:0.8rem;'>"
        "<a href='https://platform.openai.com/signup' target='_blank'"
        " style='display:inline-block; background:#c9a96e; color:#0a0a0a;"
        " font-size:0.82rem; font-weight:500; padding:0.4rem 1.2rem;"
        " border-radius:6px; text-decoration:none;'>"
        "Sign up at OpenAI &#8594;"
        "</a></div></div>",
        unsafe_allow_html=True
    )

    # Anthropic setup
    st.markdown(
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem;"
        " color:#c9a96e; font-weight:600; margin:0.5rem 0 0.6rem;'>"
        "Step 2 — Get Your Anthropic API Key (Claude)</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:12px;"
        " padding:1.4rem 1.8rem; margin-bottom:1rem;'>"
        "<div style='font-size:0.84rem; color:#888; line-height:2;'>"
        "<b style='color:#b8a88a;'>1.</b> Go to "
        "<a href='https://console.anthropic.com' target='_blank'"
        " style='color:#c9a96e;'>console.anthropic.com</a> "
        "and create a free account<br/>"
        "<b style='color:#b8a88a;'>2.</b> Click <b>API Keys</b> in the left sidebar<br/>"
        "<b style='color:#b8a88a;'>3.</b> Click <b>Create Key</b> &#8594; give it a name<br/>"
        "<b style='color:#b8a88a;'>4.</b> Copy the key — it starts with <b>sk-ant-</b><br/>"
        "<b style='color:#b8a88a;'>5.</b> Go to <b>Billing</b> &#8594; add $5 credit<br/>"
        "<b style='color:#b8a88a;'>6.</b> Paste the key in the sidebar of this app"
        "</div>"
        "<div style='margin-top:0.8rem;'>"
        "<a href='https://console.anthropic.com' target='_blank'"
        " style='display:inline-block; background:#c9a96e; color:#0a0a0a;"
        " font-size:0.82rem; font-weight:500; padding:0.4rem 1.2rem;"
        " border-radius:6px; text-decoration:none;'>"
        "Sign up at Anthropic &#8594;"
        "</a></div></div>",
        unsafe_allow_html=True
    )

    # Where to enter keys
    st.markdown(
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem;"
        " color:#c9a96e; font-weight:600; margin:0.5rem 0 0.6rem;'>"
        "Step 3 — Enter Keys in the App</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a;"
        " border-left:3px solid #c9a96e; border-radius:10px;"
        " padding:1.1rem 1.4rem;'>"
        "<div style='font-size:0.83rem; color:#888; line-height:1.85;'>"
        "Once you have both keys:<br/>"
        "&#x2022; Open the app and look at the <b style='color:#b8a88a;'>left sidebar</b><br/>"
        "&#x2022; Scroll down to <b style='color:#b8a88a;'>API Keys</b> section<br/>"
        "&#x2022; Paste your <b style='color:#b8a88a;'>OpenAI key</b> in the first box<br/>"
        "&#x2022; Paste your <b style='color:#b8a88a;'>Anthropic key</b> in the second box<br/>"
        "&#x2022; The app will use your keys automatically from that point"
        "</div></div>",
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# PRICING TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_pricing:
    st.markdown(
        "<div class='about-box'>"
        "This app is free for your first <b>5 sessions</b>. After that, you set up your own "
        "API keys and pay only for what you use. Both services are pay-as-you-go — "
        "no subscriptions, no monthly fees."
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem;"
        " color:#c9a96e; font-weight:600; margin:0.5rem 0 0.8rem;'>"
        "Cost Per Session</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:12px;"
        " padding:1.2rem 1.5rem; margin-bottom:1rem;'>"
        "<div style='font-size:0.83rem; color:#888; line-height:2;'>"
        "<div style='display:grid; grid-template-columns:2fr 1fr 1fr 1fr;"
        " gap:0.5rem; font-size:0.78rem;'>"
        "<div style='color:#c9a96e; font-weight:500;'>Audio Length</div>"
        "<div style='color:#c9a96e; text-align:right;'>Whisper</div>"
        "<div style='color:#c9a96e; text-align:right;'>Claude</div>"
        "<div style='color:#c9a96e; text-align:right;'>Total</div>"
        "<div style='color:#aaa; border-top:1px solid #2a2a2a; padding-top:6px;'>20 minutes</div>"
        "<div style='color:#aaa; text-align:right; border-top:1px solid #2a2a2a; padding-top:6px;'>~$0.12</div>"
        "<div style='color:#aaa; text-align:right; border-top:1px solid #2a2a2a; padding-top:6px;'>~$0.02</div>"
        "<div style='color:#c9a96e; text-align:right; border-top:1px solid #2a2a2a; padding-top:6px; font-weight:500;'>~$0.14</div>"
        "<div style='color:#aaa;'>1 hour</div>"
        "<div style='color:#aaa; text-align:right;'>~$0.36</div>"
        "<div style='color:#aaa; text-align:right;'>~$0.03</div>"
        "<div style='color:#c9a96e; text-align:right; font-weight:500;'>~$0.39</div>"
        "<div style='color:#aaa;'>1.5 hours</div>"
        "<div style='color:#aaa; text-align:right;'>~$0.54</div>"
        "<div style='color:#aaa; text-align:right;'>~$0.05</div>"
        "<div style='color:#c9a96e; text-align:right; font-weight:500;'>~$0.59</div>"
        "<div style='color:#aaa;'>+ Translation</div>"
        "<div style='color:#aaa; text-align:right;'>—</div>"
        "<div style='color:#aaa; text-align:right;'>~$0.05</div>"
        "<div style='color:#c9a96e; text-align:right; font-weight:500;'>~$0.05</div>"
        "</div></div></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem;"
        " color:#c9a96e; font-weight:600; margin:1rem 0 0.6rem;'>"
        "How to Get Started</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:12px;"
        " padding:1.2rem 1.5rem; margin-bottom:0.8rem;'>"
        "<div style='font-size:0.83rem; color:#888; line-height:1.9;'>"
        "<b style='color:#b8a88a;'>OpenAI (Whisper transcription)</b><br/>"
        "&#x2022; Sign up free at "
        "<a href='https://platform.openai.com/signup' target='_blank'"
        " style='color:#c9a96e;'>platform.openai.com</a><br/>"
        "&#x2022; Go to API Keys → Create key<br/>"
        "&#x2022; Add $5 credit — enough for ~35 sessions of 20-min audio<br/><br/>"
        "<b style='color:#b8a88a;'>Anthropic (Claude summarization)</b><br/>"
        "&#x2022; Sign up free at "
        "<a href='https://console.anthropic.com' target='_blank'"
        " style='color:#c9a96e;'>console.anthropic.com</a><br/>"
        "&#x2022; Go to API Keys → Create key<br/>"
        "&#x2022; Add $5 credit — enough for hundreds of summaries"
        "</div></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a;"
        " border-left:3px solid #c9a96e; border-radius:8px; padding:0.8rem 1.2rem;'>"
        "<div style='font-size:0.82rem; color:#888;'>"
        "💡 <b style='color:#b8a88a;'>Tip:</b> Set a monthly spending limit of $10 on "
        "both accounts so you are never surprised. "
        "OpenAI: Settings → Limits. Anthropic: Billing → Usage limits."
        "</div></div>",
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# FEEDBACK TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_feedback:
    st.markdown(
        "<div class='about-box'>"
        "Your feedback helps improve this app. Share your experience, suggestions, "
        "or report any issues. We read every message."
        "</div>",
        unsafe_allow_html=True
    )

    with st.form("feedback_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(
                "Your Name *",
                placeholder="e.g. Ramesh Kumar"
            )
        with col2:
            email = st.text_input(
                "Your Email Address *",
                placeholder="e.g. ramesh@gmail.com"
            )

        transcription_text = st.text_area(
            "Paste a sample of the transcription (optional)",
            placeholder="Paste a few lines from your transcription here so we can review quality...",
            height=80
        )

        col3, col4 = st.columns(2)
        with col3:
            mode_used = st.selectbox(
                "Summary mode used",
                ["Bullet highlights", "Main takeaways", "Detailed paragraphs",
                 "Executive brief", "Academic digest", "Structured table", "Full transcript"]
            )
        with col4:
            language_used = st.selectbox(
                "Language tested",
                ["English", "Hindi", "Kannada", "Telugu", "Tamil",
                 "Marathi", "Gujarati", "Other"]
            )

        rating = st.select_slider(
            "Rate your experience",
            options=["⭐ Poor", "⭐⭐ Fair", "⭐⭐⭐ Good",
                     "⭐⭐⭐⭐ Very Good", "⭐⭐⭐⭐⭐ Excellent"],
            value="⭐⭐⭐⭐⭐ Excellent"
        )

        message = st.text_area(
            "Your feedback / suggestions *",
            placeholder="Share your experience, suggestions, or any issues you faced...",
            height=100
        )

        submitted = st.form_submit_button("📧 Submit Feedback")

        if submitted:
            if not name or not email or not message:
                st.warning("⚠️ Please fill in Name, Email, and Feedback fields.")
            else:
                import urllib.parse
                subject = f"Wisdom Distiller Feedback — {mode_used} — {language_used}"
                body = (
                    f"Name: {name}\n"
                    f"Email: {email}\n"
                    f"Language tested: {language_used}\n"
                    f"Mode used: {mode_used}\n"
                    f"Rating: {rating}\n\n"
                    f"Transcription sample:\n{transcription_text or 'Not provided'}\n\n"
                    f"Feedback:\n{message}"
                )
                mailto = (
                    "mailto:vedantavani.manana@gmail.com"
                    f"?subject={urllib.parse.quote(subject)}"
                    f"&body={urllib.parse.quote(body)}"
                )
                st.success("✅ Thank you, " + name + "! Your feedback is ready to send.")
                st.markdown(
                    "<div style='background:#111; border:1px solid #2a2a2a;"
                    " border-left:3px solid #c9a96e; border-radius:8px;"
                    " padding:1rem 1.2rem; margin-top:0.5rem;'>"
                    "<div style='font-size:0.83rem; color:#aaa; margin-bottom:0.6rem;'>"
                    "Click the button below to open your email app — "
                    "your feedback is pre-filled and ready to send to "
                    "<b style='color:#c9a96e;'>vedantavani.manana@gmail.com</b>"
                    "</div>"
                    f"<a href='{mailto}' style='display:inline-block; background:#c9a96e;"
                    " color:#0a0a0a; padding:8px 20px; border-radius:8px;"
                    " text-decoration:none; font-size:0.85rem; font-weight:500;'>"
                    "📧 Open Email App to Send"
                    "</a></div>",
                    unsafe_allow_html=True
                )

# ══════════════════════════════════════════════════════════════════════════════
# SHARE TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_share:

    st.markdown(
        "<div class='about-box'>"
        "Share the Wisdom Distiller with fellow Vedantins, seekers, and anyone interested. "
        "No installation required — works on any device instantly."
        "</div>",
        unsafe_allow_html=True
    )

    # Email template
    st.markdown(
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem;"
        " color:#c9a96e; font-weight:600; margin:0.5rem 0 0.6rem;'>"
        "&#x1F4E7; Ready-to-Send Email Template</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='background:#0d0d0d; border:1px solid #1e1e1e; border-radius:10px;"
        " padding:1.2rem 1.5rem; font-size:0.82rem; color:#666;"
        " line-height:1.9; font-style:italic; margin-bottom:1rem;'>"
        "Dear [Name],<br/><br/>"
        "I would like to share a tool I have built for transcribing and summarizing "
        "spiritual discourses using AI. You can use it to get structured summaries "
        "of Vedanta lectures, Chinmaya Mission talks, Upanishad classes, and more.<br/><br/>"
        "<b style='color:#888;'>Access it here:</b> https://vedantadhara.streamlit.app<br/><br/>"
        "<b style='color:#888;'>On iPhone:</b> Open in Safari &#8594; tap Share "
        "&#8594; Add to Home Screen<br/>"
        "<b style='color:#888;'>On Android:</b> Open in Chrome &#8594; tap Menu "
        "&#8594; Add to Home Screen<br/><br/>"
        "The app is free for the first 5 uses. After that, you can set up your own "
        "API keys (instructions are inside the app under Get the App &#8594; API Setup).<br/><br/>"
        "With pranams,<br/>"
        "Dr. Suma Rajashankar"
        "</div>",
        unsafe_allow_html=True
    )

    # What they get
    st.markdown(
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem;"
        " color:#c9a96e; font-weight:600; margin:0.5rem 0 0.6rem;'>"
        "What Anyone Gets</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:10px;"
        " padding:1.1rem 1.4rem; margin-bottom:0.8rem;'>"
        "<div style='font-size:0.83rem; color:#888; line-height:1.9;'>"
        "&#x2705; <b style='color:#b8a88a;'>5 free uses</b> — no setup required<br/>"
        "&#x2705; <b style='color:#b8a88a;'>No account</b> — open and use instantly<br/>"
        "&#x2705; <b style='color:#b8a88a;'>All devices</b> — iPhone, Android, desktop<br/>"
        "&#x2705; <b style='color:#b8a88a;'>Multiple summary styles</b> — bullets, table, PDF, Word<br/>"
        "&#x2705; <b style='color:#b8a88a;'>English transliteration</b> of Sanskrit terms<br/>"
        "&#x2705; <b style='color:#b8a88a;'>Download transcripts</b> for personal study"
        "</div></div>",
        unsafe_allow_html=True
    )

    # Contact
    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a;"
        " border-left:3px solid #c9a96e; border-radius:8px;"
        " padding:0.8rem 1.2rem;'>"
        "<div style='font-size:0.82rem; color:#888;'>"
        "Questions? Reach out at "
        "<a href='mailto:vedantavani.manana@gmail.com' style='color:#c9a96e;'>"
        "vedantavani.manana@gmail.com</a>"
        "</div></div>",
        unsafe_allow_html=True
    )

