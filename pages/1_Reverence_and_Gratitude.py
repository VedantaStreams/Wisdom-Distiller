import streamlit as st
import sys
import io
from pathlib import Path
from PIL import Image, ImageOps

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

# ── CSS: force all images on this page to be circular, centered, gold border ──
st.markdown("""
<style>
[data-testid="stImage"] {
    display: flex !important;
    justify-content: center !important;
}
[data-testid="stImage"] img {
    border-radius: 50% !important;
    border: 3px solid #c9a96e !important;
    box-shadow: 0 0 24px rgba(201,169,110,0.35) !important;
    object-fit: cover !important;
    display: block !important;
    margin: 0 auto !important;
}
</style>
""", unsafe_allow_html=True)

def square_crop(path, size=300):
    """Crop image to a perfect square from the centre, return PIL Image."""
    img = Image.open(str(path)).convert("RGB")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top  = (h - side) // 2
    img  = img.crop((left, top, left + side, top + side))
    img  = img.resize((size, size), Image.LANCZOS)
    return img

def swami_label(name, subtitle, note=""):
    note_html = (
        f"<div style='font-size:0.7rem;color:#555;font-style:italic;margin-top:0.2rem;'>{note}</div>"
        if note else ""
    )
    st.markdown(
        f"<div style='text-align:center;padding:0.5rem 0 0.4rem;'>"
        f"<div style='font-family:Cormorant Garamond,serif;font-size:1.05rem;"
        f"font-weight:600;color:#e8e0d4;margin-bottom:0.1rem;'>{name}</div>"
        f"<div style='font-size:0.75rem;color:#c9a96e;letter-spacing:0.4px;'>{subtitle}</div>"
        f"{note_html}</div>",
        unsafe_allow_html=True
    )

# Image paths
om_path      = ROOT / "Om.jpeg"
gurudev_path = ROOT / "Gurudev.jpg"
aparaji_path = ROOT / "swami_aparajitananda.jpg"
sarana_path  = ROOT / "swami_sarananda.jpeg"

# ── Hero ──────────────────────────────────────────────────────────────────────
if om_path.exists():
    _, mid, _ = st.columns([2, 1, 2])
    with mid:
        st.image(str(om_path), width=80)

st.markdown("""
<div style="text-align:center;padding:0.2rem 0 0.6rem;">
    <h1 style="font-family:'Cormorant Garamond',serif;font-size:2.6rem;
    font-weight:600;color:#e8e0d4;margin:0 0 0.2rem;">
        With <span style="color:#c9a96e;">Reverence &amp; Gratitude</span>
    </h1>
</div>
<div style="text-align:center;padding:0.3rem 0 1.2rem;">
    <div style="font-size:1.2rem;color:#c9a96e;letter-spacing:6px;">✦ ✦ ✦</div>
</div>
""", unsafe_allow_html=True)

# ── Swami Chinmayananda — centred ─────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;margin-bottom:0.8rem;'>
    <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
    letter-spacing:1.5px;'>In Devotion &amp; Remembrance</div>
</div>""", unsafe_allow_html=True)

_, mid, _ = st.columns([1.5, 1, 1.5])
with mid:
    if gurudev_path.exists():
        gurudev_sq = square_crop(gurudev_path, size=300)
        st.image(gurudev_sq, width=190)
    swami_label(
        "Pūjya Swāmī Chinmayānandajī",
        "Founder · Chinmaya Mission",
        note="May his eternal light guide all seekers"
    )

st.markdown("<hr style='border-color:#1e1e1e;margin:1rem 0 1.2rem;'/>", unsafe_allow_html=True)

# ── Aparājitānandajī & Śaraṇānandajī — side by side, perfectly aligned ────────
st.markdown("""
<div style='text-align:center;margin-bottom:0.8rem;'>
    <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
    letter-spacing:1.5px;'>With Deep Gratitude &amp; Humble Pranāms</div>
</div>""", unsafe_allow_html=True)

# Use base64 for both images rendered inside pure HTML so alignment is pixel-perfect
import base64 as _b64

def _img_src(path, size=300):
    img = square_crop(path, size)
    buf = __import__('io').BytesIO()
    img.save(buf, format='JPEG', quality=90)
    return "data:image/jpeg;base64," + _b64.b64encode(buf.getvalue()).decode()

aparaji_src = _img_src(aparaji_path) if aparaji_path.exists() else ""
sarana_src  = _img_src(sarana_path)  if sarana_path.exists()  else ""

circle_style = (
    "width:165px;height:165px;object-fit:cover;border-radius:50%;"
    "border:3px solid #c9a96e;box-shadow:0 0 24px rgba(201,169,110,0.35);"
    "display:block;margin:0 auto 0.7rem;"
)

st.markdown(f"""
<div style='display:flex;justify-content:center;align-items:flex-start;
            gap:80px;padding:0.5rem 0 1rem;'>
  <div style='text-align:center;flex:0 0 auto;'>
    <img src='{aparaji_src}' style='{circle_style}'/>
    <div style='font-family:Cormorant Garamond,serif;font-size:1.05rem;
    font-weight:600;color:#e8e0d4;margin-bottom:0.1rem;'>Swāmī Aparājitānandajī</div>
    <div style='font-size:0.75rem;color:#c9a96e;letter-spacing:0.4px;'>Chinmaya Mission</div>
  </div>
  <div style='text-align:center;flex:0 0 auto;'>
    <img src='{sarana_src}' style='{circle_style}'/>
    <div style='font-family:Cormorant Garamond,serif;font-size:1.05rem;
    font-weight:600;color:#e8e0d4;margin-bottom:0.1rem;'>Swāmī Śaraṇānandajī</div>
    <div style='font-size:0.75rem;color:#c9a96e;letter-spacing:0.4px;'>Chinmaya Mission</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border-color:#1e1e1e;margin:1.5rem 0;'/>", unsafe_allow_html=True)

# ── Pranams text ──────────────────────────────────────────────────────────────
st.markdown("""
<div style='max-width:700px;margin:0 auto;'>
<div style='background:#111;border:1px solid #2a2a2a;border-left:3px solid #c9a96e;
border-radius:12px;padding:2rem 2.4rem;margin-bottom:1.5rem;'>

<div style='font-family:Cormorant Garamond,serif;font-size:1.1rem;color:#c9a96e;
font-weight:600;letter-spacing:0.5px;margin-bottom:1.4rem;'>🔹 Pranāms &amp; Gratitude</div>

<div style='font-size:0.93rem;color:#aaa;line-height:2;font-style:italic;margin-bottom:1.2rem;'>
With deep reverence and devotion, I offer my humble pranāms and heartfelt gratitude to
<span style='color:#c9a96e;font-style:normal;font-weight:500;'>Swāmī Aparājitānandajī</span>
and
<span style='color:#c9a96e;font-style:normal;font-weight:500;'>Swāmī Śaraṇānandajī</span>.
</div>

<div style='font-size:0.93rem;color:#999;line-height:2;margin-bottom:1.2rem;
border-top:1px solid #1e1e1e;padding-top:1.1rem;'>
To <span style='color:#b8a88a;font-weight:500;'>Pūjya Swāmī Aparājitānandajī</span>,
I offer sincere gratitude for his extraordinary ability to unfold the profound and subtle truths
of Vedānta with remarkable clarity, precision, and simplicity. Through his illuminating discourses,
even the most intricate philosophical concepts become accessible and relatable to seekers from all
walks of life. His tireless dedication to preserving and sharing the wisdom of the scriptures
continues to inspire deeper inquiry, reflection, and understanding.
</div>

<div style='font-size:0.93rem;color:#999;line-height:2;margin-bottom:1.2rem;
border-top:1px solid #1e1e1e;padding-top:1.1rem;'>
To <span style='color:#b8a88a;font-weight:500;'>Pūjya Swāmī Śaraṇānandajī</span>,
I offer heartfelt gratitude for his boundless compassion, humility, and love, which shine
effortlessly through both his teachings and his very way of living. He stands as a living
embodiment of surrender, simplicity, devotion, and grace. His gentle guidance and heartfelt
exposition of the scriptures touch seekers deeply, nurturing not only understanding but also
inner transformation, devotion, and spiritual strength.
</div>

<div style='font-family:Cormorant Garamond,serif;font-size:0.97rem;color:#c9a96e;
line-height:2;font-style:italic;border-top:1px solid #1e1e1e;padding-top:1.1rem;
margin-bottom:1.2rem;'>
This humble initiative is offered as a small <span style='font-style:normal;'>seva</span>
at their holy feet — an effort to preserve, organize, and share the invaluable wisdom
flowing through their discourses so that more seekers may listen
(<span style='font-style:normal;'>śravaṇa</span>), reflect
(<span style='font-style:normal;'>manana</span>), and internalize these sacred teachings
(<span style='font-style:normal;'>nididhyāsana</span>) with greater ease, devotion, and depth.
</div>

<div style='font-size:0.88rem;color:#666;line-height:2;border-top:1px solid #1e1e1e;
padding-top:1rem;font-style:italic;'>
I also offer reverential gratitude to the sacred
<span style='color:#b8a88a;font-style:normal;'>Guru–Śiṣya Paramparā</span>
and the great lineage of teachers through whom this timeless wisdom continues to illumine
countless seekers across generations.
</div>

</div></div>
""", unsafe_allow_html=True)

# ── Quote ──────────────────────────────────────────────────────────────────────
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

