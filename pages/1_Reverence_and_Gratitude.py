import streamlit as st
import base64
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from utils.styles import SHARED_CSS, LIGHT_CSS

st.set_page_config(
    page_title="Reverence & Gratitude · Wisdom Distiller",
    page_icon="🙏",
    layout="centered"
)
_theme_css = SHARED_CSS if st.session_state.get("theme","dark") == "dark" else LIGHT_CSS
st.markdown(_theme_css, unsafe_allow_html=True)


# ── Load Om image ──────────────────────────────────────────────────────────────
def img_b64(path: str, mime: str = "image/jpeg") -> str:
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"

om_path = Path(__file__).parent.parent / "Om.jpeg"
om_tag = f'<img class="om" src="{img_b64(str(om_path))}" alt="Om"/>' if om_path.exists() else "🕉️"


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    {om_tag}
    <h1>With <span class="accent">Reverence &amp; Gratitude</span></h1>
</div>
""", unsafe_allow_html=True)


# ── Decorative divider ─────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 0.5rem 0 1.5rem;">
    <div style="font-size:1.3rem; color:#c9a96e; letter-spacing:6px;">✦ ✦ ✦</div>
</div>
""", unsafe_allow_html=True)


# ── Pranams block ──────────────────────────────────────────────────────────────
st.markdown(
    "<div style='max-width:680px; margin:0 auto;'>"

    # ── Main card ──────────────────────────────────────────────────────────────
    "<div style='background:#111; border:1px solid #2a2a2a; border-left:3px solid #c9a96e;"
    " border-radius:12px; padding:2rem 2.2rem; margin-bottom:1.5rem;'>"

    "<div style='font-family:Cormorant Garamond,serif; font-size:1.1rem;"
    " color:#c9a96e; font-weight:600; letter-spacing:0.5px; margin-bottom:1.4rem;'>"
    "🔹 Pranāms &amp; Gratitude"
    "</div>"

    # Opening salutation
    "<div style='font-size:0.95rem; color:#aaa; line-height:2; font-style:italic;"
    " margin-bottom:1rem;'>"
    "With deep reverence, I offer my humble pranāms and heartfelt gratitude to "
    "<span style='color:#c9a96e; font-style:normal; font-weight:500;'>"
    "Swami Aparājitānandajī</span> and "
    "<span style='color:#c9a96e; font-style:normal; font-weight:500;'>"
    "Swāmī Śaraṇānandajī</span>."
    "</div>"

    # Para 1
    "<div style='font-size:0.92rem; color:#999; line-height:2; margin-bottom:1rem;"
    " border-top:1px solid #1e1e1e; padding-top:1rem;'>"
    "Their illuminating discourses, compassionate guidance, and unwavering dedication "
    "to the sacred "
    "<span style='color:#b8a88a;'>Guru–Śiṣya Paramparā</span> "
    "continue to inspire and shape this humble effort."
    "</div>"

    # Para 2
    "<div style='font-size:0.92rem; color:#999; line-height:2; margin-bottom:1rem;'>"
    "The clarity with which they unfold the timeless wisdom of "
    "<span style='color:#b8a88a;'>Vedanta</span>, "
    "along with their tireless commitment to making these teachings accessible "
    "to sincere seekers, forms the very foundation of this discourse summary app."
    "</div>"

    # Para 3 — offering
    "<div style='font-family:Cormorant Garamond,serif; font-size:1rem; color:#c9a96e;"
    " line-height:2; font-style:italic; border-top:1px solid #1e1e1e; padding-top:1rem;'>"
    "This initiative is but a small offering — an attempt to distill, preserve, "
    "and share their profound insights — so that more seekers may listen, "
    "reflect (<span style='font-style:normal;'>manana</span>), and internalize "
    "these teachings with greater ease, devotion, and depth."
    "</div>"

    "</div></div>",
    unsafe_allow_html=True
)


# ── Quote block ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="max-width:660px; margin: 0 auto;">
    <div style="background:#0d0d0d; border:1px solid #1e1e1e; border-radius:12px;
                padding:1.8rem 2rem; text-align:center;">
        <div style="font-family:'Cormorant Garamond',serif; font-style:italic;
                    font-size:1.1rem; color:#c9a96e; line-height:1.9;">
            "Renounce your ego" is the Lord's only request;<br/>
            "And I will make you God" is the promise.
        </div>
        <div style="font-family:'Cormorant Garamond',serif; font-size:1.05rem;
                    color:#c9a96e; font-style:italic; margin-top:0.8rem;">
            — <em>Pūjya Swāmī Chinmayānanda</em>
        </div>
        <div style="font-size:0.75rem; color:#555; margin-top:0.3rem;
                    font-style:italic; letter-spacing:0.3px;">
            (Pūjya Swāmī Chinmayānanda — the Bliss of Pure Consciousness)
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Bottom lotus ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem;">
    <div style="font-size:1.3rem; letter-spacing:8px;">🪷 🕉️ 🪷</div>
</div>
""", unsafe_allow_html=True)
