import streamlit as st
import base64
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from utils.styles import SHARED_CSS

st.set_page_config(page_title="Sādhanā & Seva · Wisdom Distiller", page_icon="🕉️", layout="centered")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── Home button in sidebar ────────────────────────────────────────────────────
with st.sidebar:
    try:
        st.page_link("app.py", label="🏠 Home")
    except Exception:
        if st.button("🏠 Home", key="home_btn_" + __file__[-20:]):
            st.switch_page("app.py")
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>", unsafe_allow_html=True)


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

</div>
<hr style="border-color:#1e1e1e; margin: 1.2rem 0;"/>
""", unsafe_allow_html=True)

# ── Bio paragraphs ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="max-width:680px; margin: 0 auto; font-size:0.95rem; color:#999; line-height:1.95;">

<p>My name is <b style="color:#b8a88a;">Suma Rajashankar</b>. I am a sincere student and
earnest seeker of Vedānta, deeply grateful for the opportunity to learn from the timeless
wisdom of the scriptures and the guidance of revered Gurus and teachers. Though my
professional journey has been across the fields of Physics, academia, Data Science,
Machine Learning, and Generative AI, my deepest inspiration continues to come from the
study of Vedānta and the lifelong path of spiritual learning.</p>

<p>By the grace of many teachers and mentors, I have been blessed with opportunities to
study, teach, research, and serve in both academia and industry. I hold a
<b style="color:#b8a88a;">PhD in Physics from the Indian Institute of Science</b> and
spent many years teaching and mentoring students in engineering and science. I currently
work in the field of AI and Data Science as a
<b style="color:#b8a88a;">Senior Data Scientist / AI Engineer</b> at
<a href="https://www.capitalone.com" target="_blank"
   style="color:#c9a96e; text-decoration:none; border-bottom:1px dashed #c9a96e;">Capital One</a>,
focusing on machine learning, generative AI, and enterprise AI systems. Alongside my
professional work, I have also been grateful for opportunities to mentor and guide working
professionals in AI and Machine Learning — a small way of sharing knowledge and continuing
my love for teaching and learning.</p>

<p>Yet beyond all professional roles and accomplishments, it is the study of Vedānta and
the sacred <b style="color:#b8a88a;">Guru–Śiṣya Paramparā</b> that I hold closest to my
heart. Through satsangs, scriptural study, contemplation, and the grace of my revered Gurus,
I continue this lifelong journey of learning through the
<b style="color:#b8a88a;">Upaniṣads</b>,
<b style="color:#b8a88a;">Bhagavad Gītā</b>, and
<b style="color:#b8a88a;">Prakaraṇa Granthas</b>. The teachings of the scriptures, along
with the guidance of revered teachers through the
<b style="color:#b8a88a;">Chinmaya Mission</b>, continue to shape my understanding of
life, knowledge, purpose, and seva.</p>

<p>This humble initiative was born from a simple and heartfelt desire — to use modern AI
tools in service of making sacred discourse wisdom more accessible to seekers. The purpose
of this app is to assist in <b style="color:#b8a88a;">transcribing discourses</b>,
generating summaries for reflection and note-taking,
<b style="color:#b8a88a;">extracting meaningful quotes and insights</b>, and making
these teachings accessible across different languages and formats.</p>

<p style="font-family:'Cormorant Garamond',serif; font-style:italic; color:#888; font-size:0.97rem;">
This app is offered as a small <span style="font-style:normal;">seva</span>, with the hope
that it may help listeners revisit, reflect upon, organize, and internalize the wisdom shared
in these sacred discourses with greater ease, clarity, and devotion. I remain deeply grateful
to the teachers, seekers, and the
<b style="color:#b8a88a; font-style:normal;">Chinmaya Mission</b> family whose guidance,
inspiration, and blessings continue to make this humble offering possible.</p>

</div>
<hr style="border-color:#1e1e1e; margin: 1.5rem auto; max-width:680px;"/>
""", unsafe_allow_html=True)

# ── Stats ────────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
for col, num, label in [
    (c1, "350+", "Professionals Mentored"),
    (c2, "300+", "Hours of AI/ML Instruction"),
    (c3, "4.75–5.0", "Mentor Rating (4 Years)"),
]:
    with col:
        st.markdown(f"""
        <div style="background:#111; border:1px solid #2a2a2a; border-top:3px solid #c9a96e;
                    border-radius:10px; padding:1.2rem; text-align:center; margin-bottom:1rem;">
            <div style="font-family:'Cormorant Garamond',serif; font-size:2rem;
                        font-weight:600; color:#c9a96e;">{num}</div>
            <div style="font-size:0.75rem; color:#666; text-transform:uppercase;
                        letter-spacing:0.5px;">{label}</div>
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
