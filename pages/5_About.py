import streamlit as st
import base64
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from utils.styles import SHARED_CSS, LIGHT_CSS

st.set_page_config(page_title="About · Wisdom Distiller", page_icon="🕉️", layout="centered")
_theme_css = SHARED_CSS if st.session_state.get("theme","dark") == "dark" else LIGHT_CSS
st.markdown(_theme_css, unsafe_allow_html=True)

def img_b64(path: str, mime: str = "image/jpeg") -> str:
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"

om_path = Path(__file__).parent.parent / "Om.jpeg"
headshot_path = Path(__file__).parent.parent / "headshot.jpeg"

om_tag = f'<img class="om" src="{img_b64(str(om_path))}" alt="Om"/>' if om_path.exists() else "🕉️"

if headshot_path.exists():
    hs_src = img_b64(str(headshot_path))
    headshot_html = f'<img src="{hs_src}" alt="Suma Rajashankar" style="width:180px;height:180px;border-radius:50%;object-fit:cover;border:3px solid #c9a96e;display:block;margin:0 auto 1rem;box-shadow:0 0 28px rgba(201,169,110,0.35);"/>'
else:
    headshot_html = '<div style="width:160px;height:160px;border-radius:50%;background:#1e1e1e;border:2px solid #c9a96e;display:flex;align-items:center;justify-content:center;font-family:Cormorant Garamond,serif;font-size:2rem;color:#c9a96e;margin:0 auto 1rem;">SR</div>'

st.markdown(f"""
<div class="hero">
    {om_tag}
    <div style="font-family:'Cormorant Garamond',serif; font-size:1.6rem; font-weight:600; color:#c9a96e; margin:0.3rem 0 0.2rem; letter-spacing:0.5px;">A Seeker's Journey</div>
    <div style="font-family:'Cormorant Garamond',serif; font-style:italic;
                font-size:1.05rem; color:#c9a96e; letter-spacing:1px; margin:0.4rem 0 0.2rem;">
        &#x15A;rava&#x1E47;a &middot; Manana &middot; Nididhy&#x101;sana
    </div>
    <div style="font-size:0.82rem; color:#aaa; letter-spacing:0.8px;
                font-style:italic; margin-bottom:0.3rem;">
        Listening &middot; Reflection &middot; Contemplation
    </div>
    <div style="font-family:'Cormorant Garamond',serif; font-style:italic;
                font-size:1rem; color:#c9a96e; max-width:500px; margin:0.4rem auto 0;
                line-height:1.8;">
        &#x924;&#x924;&#x94D;&#x924;&#x94D;&#x935;&#x92E;&#x938;&#x93F;
        <span style="font-size:0.82rem; color:#aaa; font-style:italic;">
            &mdash; Tat tvam asi &middot; That thou art
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="text-align:center; padding: 1.5rem 0 0.5rem;">
    {headshot_html}
    <div style="font-family:'Cormorant Garamond',serif; font-size:1.2rem; font-weight:600; color:#e8e0d4;">Suma Rajashankar</div>
    <div style="font-size:0.85rem; color:#c9a96e; letter-spacing:0.8px; text-transform:uppercase; margin-top:0.3rem;">
        Senior Data Scientist / AI Engineer · Capital One
    </div>
</div>
<hr style="border-color:#1e1e1e; margin: 1.2rem 0;"/>
""", unsafe_allow_html=True)

# ── Bio paragraphs ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="max-width:680px; margin: 0 auto; font-size:0.95rem; color:#999; line-height:1.85;">

<p>Suma Rajashankar holds a <b style="color:#b8a88a;">PhD in Physics</b> from the Indian Institute
of Science and completed postdoctoral research at <b style="color:#b8a88a;">Stony Brook University</b>.
She served as an <b style="color:#b8a88a;">Assistant Professor</b> at Northern Illinois University,
teaching across Electrical and Industrial Engineering disciplines for over
<b style="color:#b8a88a;">18 years</b>.</p>

<p>Wishing to broaden her horizons and gain experience beyond academia, she transitioned into the
<b style="color:#b8a88a;">corporate world</b> — bringing her deep academic foundation into the field
of <b style="color:#b8a88a;">AI and Data Science</b>. She has since contributed to impactful work at
<b style="color:#b8a88a;">Discover Financial Services</b> and currently at
<b style="color:#b8a88a;">Capital One</b>, spanning Generative AI, Speech Recognition, and
Responsible AI — including the development of guardrails for enterprise-scale AI engineering
platforms.</p>

<p>She considers herself a <b style="color:#b8a88a;">humble and earnest seeker on the spiritual
path</b>, and a <b style="color:#b8a88a;">devoted student of Vedanta</b>, blessed to be closely
associated with the <b style="color:#b8a88a;">Chinmaya Mission</b>. Through study groups,
satsangs, and the systematic study of the Upanishads, the Bhagavad Gita, and the Prakarana
Granthas, this remains a personal journey of reflection, gratitude, and grace.</p>

<p>She also guides working professionals through <b style="color:#b8a88a;">AIML and AIDL programs</b>
in collaboration with the <b style="color:#b8a88a;">University of Texas at Austin</b> and
<b style="color:#b8a88a;">Great Learning</b> — a small way of giving back.</p>

</div>
<hr style="border-color:#1e1e1e; margin: 1.5rem auto; max-width:680px;"/>
""", unsafe_allow_html=True)

# ── Stats ──────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
for col, num, label in [
    (c1, "350+", "Professionals Mentored"),
    (c2, "400+", "Hours of AI/ML Instruction"),
    (c3, "4.75–5.0", "Mentor Rating (4 Years)"),
]:
    with col:
        st.markdown(f"""
        <div style="background:#111; border:1px solid #2a2a2a; border-top:3px solid #c9a96e;
                    border-radius:10px; padding:1.2rem; text-align:center;">
            <div style="font-family:'Cormorant Garamond',serif; font-size:2rem; font-weight:600; color:#c9a96e;">{num}</div>
            <div style="font-size:0.75rem; color:#666; text-transform:uppercase; letter-spacing:0.5px;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Contact ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="max-width:680px; margin: 0 auto 1.5rem; text-align:center;">
    <div style="background:#111; border:1px solid #2a2a2a; border-radius:10px;
                padding:1rem 1.5rem; display:inline-block;">
        <div style="font-size:0.78rem; color:#666; text-transform:uppercase;
                    letter-spacing:0.8px; margin-bottom:0.4rem;">📬 Contact</div>
        <a href="mailto:vedantavani.manana@gmail.com"
           style="font-family:'Cormorant Garamond',serif; font-size:1rem;
                  color:#c9a96e; text-decoration:none; letter-spacing:0.3px;">
            vedantavani.manana@gmail.com
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Quote with styled Swamiji name ────────────────────────────────────────────
st.markdown("""
<hr style="border-color:#1e1e1e; margin: 1.5rem 0;"/>
<div style="text-align:center; padding: 0.5rem 0 1.5rem;">
    <div style="font-family:'Cormorant Garamond',serif; font-style:italic; font-size:1.15rem; color:#c9a96e; line-height:1.8;">
        "Renounce your ego" is the Lord's only request;<br/>
        "And I will make you God" is the promise.
    </div>
    <div style="font-family:'Cormorant Garamond',serif; font-size:1.05rem; color:#c9a96e;
                font-style:italic; letter-spacing:0.5px; margin-top:0.6rem;">
        — <em>Pūjya Swāmī Chinmayānanda</em>
    </div>
    <div style="font-size:0.75rem; color:#555; margin-top:0.2rem; font-style:italic; letter-spacing:0.3px;">
        (Pūjya Swāmī Chinmayānanda — the Bliss of Pure Consciousness)
    </div>
</div>
""", unsafe_allow_html=True)
