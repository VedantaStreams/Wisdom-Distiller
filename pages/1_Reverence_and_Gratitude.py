import streamlit as st
import base64
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from utils.styles import SHARED_CSS

st.set_page_config(
    page_title="Reverence & Gratitude · Wisdom Distiller",
    page_icon="🙏",
    layout="centered"
)
st.markdown(SHARED_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.page_link("app.py", label="🏠 Home")
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def img_b64(path: str) -> str:
    ext = Path(path).suffix.lower()
    mime = "image/png" if ext == ".png" else ("image/jpeg" if ext in (".jpg",".jpeg") else "image/jpeg")
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"

def swami_card(img_path, name, subtitle, note="", size=160):
    src = img_b64(img_path) if img_path and Path(img_path).exists() else None
    if src:
        img_html = (
            f"<img src='{src}' style='width:{size}px;height:{size}px;"
            f"object-fit:cover;object-position:center top;"
            f"border-radius:50%;border:3px solid #c9a96e;"
            f"box-shadow:0 0 24px rgba(201,169,110,0.35);display:block;margin:0 auto 0.9rem;'/>"
        )
    else:
        img_html = (
            f"<div style='width:{size}px;height:{size}px;border-radius:50%;"
            f"border:3px solid #c9a96e;background:#1a1a1a;"
            f"display:flex;align-items:center;justify-content:center;"
            f"font-size:3rem;margin:0 auto 0.9rem;'>🕉️</div>"
        )
    note_html = (
        f"<div style='font-size:0.7rem;color:#555;margin-top:0.25rem;"
        f"font-style:italic;'>{note}</div>"
    ) if note else ""
    return (
        f"<div style='text-align:center;padding:0.8rem 0.5rem;'>"
        f"{img_html}"
        f"<div style='font-family:Cormorant Garamond,serif;font-size:1.05rem;"
        f"font-weight:600;color:#e8e0d4;margin-bottom:0.15rem;'>{name}</div>"
        f"<div style='font-size:0.75rem;color:#c9a96e;letter-spacing:0.4px;'>{subtitle}</div>"
        f"{note_html}"
        f"</div>"
    )

# Image paths
om_path       = ROOT / "Om.jpeg"
gurudev_path  = ROOT / "Gurudev.jpg"               # Swami Chinmayananda
aparaji_path  = ROOT / "swami_aparajitananda.jpg"  # Swami Aparājitānandajī
sarana_path   = ROOT / "swami_sarananda.jpeg"      # Swami Śaraṇānandajī

# ── Hero ──────────────────────────────────────────────────────────────────────
om_tag = (
    f'<img class="om" src="{img_b64(str(om_path))}" alt="Om"/>' 
    if om_path.exists() else "🕉️"
)
st.markdown(f"""
<div class="hero">
    {om_tag}
    <h1>With <span class="accent">Reverence &amp; Gratitude</span></h1>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:0.5rem 0 1.2rem;">
    <div style="font-size:1.2rem;color:#c9a96e;letter-spacing:6px;">✦ ✦ ✦</div>
</div>
""", unsafe_allow_html=True)

# ── Swami Chinmayananda — centred, larger ─────────────────────────────────────
st.markdown("""
<div style='text-align:center;margin-bottom:0.6rem;'>
    <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
    letter-spacing:1.5px;'>In Devotion &amp; Remembrance</div>
</div>""", unsafe_allow_html=True)

col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    st.markdown(swami_card(
        str(gurudev_path),
        "Pūjya Swāmī Chinmayānandajī",
        "Founder · Chinmaya Mission",
        note="May his eternal light guide all seekers",
        size=190
    ), unsafe_allow_html=True)

st.markdown("<hr style='border-color:#1e1e1e;margin:1rem 0 1.2rem;'/>", unsafe_allow_html=True)

# ── Aparājitānandajī & Śaraṇānandajī side by side ────────────────────────────
st.markdown("""
<div style='text-align:center;margin-bottom:0.6rem;'>
    <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
    letter-spacing:1.5px;'>With Deep Gratitude &amp; Humble Pranāms</div>
</div>""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown(swami_card(
        str(aparaji_path),
        "Swami Aparājitānandajī",
        "Chinmaya Mission",
        size=165
    ), unsafe_allow_html=True)
with col2:
    st.markdown(swami_card(
        str(sarana_path),
        "Swāmī Śaraṇānandajī",
        "Chinmaya Mission",
        size=165
    ), unsafe_allow_html=True)

st.markdown("<hr style='border-color:#1e1e1e;margin:1.5rem 0;'/>", unsafe_allow_html=True)

# ── Pranams text ──────────────────────────────────────────────────────────────
st.markdown(
    "<div style='max-width:680px;margin:0 auto;'>"
    "<div style='background:#111;border:1px solid #2a2a2a;border-left:3px solid #c9a96e;"
    "border-radius:12px;padding:2rem 2.2rem;margin-bottom:1.5rem;'>"
    "<div style='font-family:Cormorant Garamond,serif;font-size:1.1rem;"
    "color:#c9a96e;font-weight:600;letter-spacing:0.5px;margin-bottom:1.4rem;'>🔹 Pranāms &amp; Gratitude</div>"
    "<div style='font-size:0.95rem;color:#aaa;line-height:2;font-style:italic;margin-bottom:1rem;'>"
    "With deep reverence, I offer my humble pranāms and heartfelt gratitude to "
    "<span style='color:#c9a96e;font-style:normal;font-weight:500;'>Swami Aparājitānandajī</span>"
    " and <span style='color:#c9a96e;font-style:normal;font-weight:500;'>Swāmī Śaraṇānandajī</span>."
    "</div>"
    "<div style='font-size:0.92rem;color:#999;line-height:2;margin-bottom:1rem;"
    "border-top:1px solid #1e1e1e;padding-top:1rem;'>"
    "Their illuminating discourses, compassionate guidance, and unwavering dedication to the sacred "
    "<span style='color:#b8a88a;'>Guru–Śiṣya Paramparā</span> continue to inspire and shape this humble effort."
    "</div>"
    "<div style='font-size:0.92rem;color:#999;line-height:2;margin-bottom:1rem;'>"
    "The clarity with which they unfold the timeless wisdom of <span style='color:#b8a88a;'>Vedanta</span>, "
    "along with their tireless commitment to making these teachings accessible to sincere seekers, "
    "forms the very foundation of this discourse summary app."
    "</div>"
    "<div style='font-family:Cormorant Garamond,serif;font-size:1rem;color:#c9a96e;"
    "line-height:2;font-style:italic;border-top:1px solid #1e1e1e;padding-top:1rem;'>"
    "This initiative is but a small offering — an attempt to distill, preserve, and share their profound insights — "
    "so that more seekers may listen, reflect (<span style='font-style:normal;'>manana</span>), "
    "and internalize these teachings with greater ease, devotion, and depth."
    "</div>"
    "</div></div>",
    unsafe_allow_html=True
)

# ── Quote block ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="max-width:660px;margin:0 auto;">
    <div style="background:#0d0d0d;border:1px solid #1e1e1e;border-radius:12px;
                padding:1.8rem 2rem;text-align:center;">
        <div style="font-family:'Cormorant Garamond',serif;font-style:italic;
                    font-size:1.1rem;color:#c9a96e;line-height:1.9;">
            "Renounce your ego" is the Lord's only request;<br/>
            "And I will make you God" is the promise.
        </div>
        <div style="font-family:'Cormorant Garamond',serif;font-size:1rem;
                    color:#c9a96e;font-style:italic;margin-top:0.8rem;">
            — <em>Pūjya Swāmī Chinmayānandajī</em>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;">
    <div style="font-size:1.3rem;letter-spacing:8px;">🪷 🕉️ 🪷</div>
</div>
""", unsafe_allow_html=True)

