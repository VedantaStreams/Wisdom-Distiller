import streamlit as st
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="About the App · Wisdom Distiller",
    page_icon="🕉️",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils.styles import SHARED_CSS
st.markdown(SHARED_CSS, unsafe_allow_html=True)

with st.sidebar:
    try:
        st.page_link("app.py", label="🏠 Home")
    except Exception:
        pass
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🕉️ About <span class="accent">Wisdom Distiller</span></h1>
    <p class="subtitle">What makes this app different</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='max-width:700px; margin: 1rem auto 0;'>
<div style='background:#111; border:1px solid #2a2a2a; border-left:3px solid #c9a96e;
border-radius:12px; padding:1.4rem 1.8rem; margin-bottom:1.5rem;
font-size:0.93rem; color:#999; line-height:1.9; font-style:italic;'>
Wisdom Distiller is not a generic AI tool repurposed for spiritual content.
It was designed from the ground up — with intentionality, reverence, and deep familiarity
with the Vedantic tradition — to serve sincere seekers of the timeless wisdom of the scriptures.
</div>
</div>
""", unsafe_allow_html=True)

# ── Unique features ───────────────────────────────────────────────────────────
features = [
    (
        "🕉️",
        "Built Exclusively for Vedantic Discourses",
        "Unlike generic transcription tools, every prompt in this app is written with "
        "deep familiarity with Vedānta, Sanskrit terminology, scriptural references, and "
        "the Guru–Śiṣya teaching tradition. The AI understands the difference between "
        "Karma Kāṇḍa and Jñāna Kāṇḍa, recognizes Upaniṣadic verses, and responds with "
        "the reverence these teachings deserve."
    ),
    (
        "Sanskrit in Devanāgarī — Always",
        "देवनागरी",
        "Every other AI tool either drops Sanskrit or transliterates it into Roman script. "
        "This app is specifically instructed to always render Sanskrit verses in authentic "
        "Devanāgarī script (e.g. श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात्) — "
        "preserving the scriptural authenticity that no other tool maintains."
    ),
    (
        "🌐",
        "Seven Indian Languages",
        "English, Hindi, Kannada, Telugu, Tamil, Marathi, and Gujarati — with proper "
        "Unicode rendering in the UI and in all exported documents. Most tools support "
        "only English or major world languages, leaving regional seekers underserved."
    ),
    (
        "📋",
        "Six Output Formats for Every Kind of Seeker",
        "Bullet Highlights · Main Takeaways · Detailed Paragraphs · Executive Brief · "
        "Academic Digest · Structured Table — each designed for a different purpose: "
        "quick review, deep study, social sharing, classroom use, or personal archiving."
    ),
    (
        "💎",
        "Wisdom Extractor — Verbatim Quote Curation",
        "No other tool extracts verbatim quotes from spiritual discourses with thematic "
        "tagging (Ātman, Devotion, Ego, Karma, Knowledge etc.), generates YouTube titles, "
        "reel captions, and hashtags — all specifically tuned for Vedantic content and "
        "social media outreach."
    ),
    (
        "📜",
        "Discourse Transcriber with Full Structured Output",
        "Not just a raw transcript — the AI organizes every sentence into meaningful "
        "sections (Introduction, Main Teaching, Scriptural Explanation, Story/Analogy, "
        "Practical Application) with a Sanskrit glossary and reflection at the end. "
        "Purpose-built for archiving and studying sacred teachings."
    ),
    (
        "✦",
        "Discourse Details Header on Every Output",
        "Every summary, transcript, and quote extraction includes a structured metadata "
        "header: Speaker · Topic · Scripture · Language · Verses Referenced · Key Sanskrit "
        "Terms — creating a proper, organized archival record of each discourse."
    ),
    (
        "📥",
        "Export to TXT, PDF, and DOCX",
        "With full formatting preserved — bold headings, Sanskrit fonts, bullet points, "
        "and tables. Most AI tools export plain text only, losing all structure in the process."
    ),
    (
        "🎙️",
        "Multi-File Audio Support",
        "Upload up to 5 audio segments that are stitched into one unified transcript and "
        "summary — ideal for long discourses recorded across multiple sittings or days."
    ),
    (
        "🪷",
        "Personal Reflection Journal — Manana & Nididhyāsana",
        "Every output page includes a dedicated <b>My Reflections</b> space — a quiet "
        "corner for the seeker to capture their own notes, questions, insights, and "
        "contemplations right alongside the AI-generated content. When downloaded, "
        "the reflection is included at the end of the PDF or DOCX — creating a complete "
        "personal study document that combines the wisdom of the discourse with the "
        "seeker's own inquiry. This directly supports the three stages of Vedantic "
        "learning: Śravaṇa (listening), Manana (reflection), and Nididhyāsana "
        "(deep contemplation)."
    ),
    (
        "🎯",
        "Custom Focus Prompt — Direct the AI's Attention",
        "A unique feature of the Discourse Transcriber — you can give the AI specific "
        "instructions about what to look for and highlight in the transcript. For example: "
        "<i>'Highlight the areas where Swamiji has stressed key points'</i> or "
        "<i>'Identify all places where other scriptural texts are referenced'</i>. "
        "The AI then annotates the transcript inline with bold labels like "
        "<b>[KEY EMPHASIS]</b>, <b>[CROSS-REFERENCE: Bhagavatam]</b>, and <b>[ANALOGY]</b> "
        "— making it effortless to find exactly what you are looking for in a long discourse. "
        "No other spiritual AI tool offers this level of guided, personalized attention."
    ),
    (
        "🙏",
        "Built with Devotion — Offered as Seva",
        "No advertisements. No data stored between sessions. No subscription tiers or "
        "paywalls. This app is offered freely as a small seva at the feet of the teachers "
        "— in the spirit of the very teachings it serves."
    ),
]

st.markdown("<div style='max-width:700px; margin: 0 auto;'>", unsafe_allow_html=True)

for icon, title, desc in features:
    st.markdown(f"""
    <div style='background:#111; border:1px solid #1e1e1e; border-left:3px solid #c9a96e;
    border-radius:10px; padding:1.2rem 1.5rem; margin-bottom:1rem;'>
        <div style='display:flex; align-items:flex-start; gap:0.8rem;'>
            <div style='font-size:1.3rem; min-width:2rem; text-align:center;
            color:#c9a96e; font-family:serif;'>{icon}</div>
            <div>
                <div style='font-family:Cormorant Garamond,serif; font-size:1.05rem;
                font-weight:600; color:#e8e0d4; margin-bottom:0.4rem;'>{title}</div>
                <div style='font-size:0.88rem; color:#888; line-height:1.8;'>{desc}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── Prompt engineering note ───────────────────────────────────────────────────
st.markdown("""
<div style='max-width:700px; margin: 1.5rem auto 0;'>
<div style='background:#0d0d0d; border:1px solid #1e1e1e; border-radius:12px;
padding:1.6rem 2rem; text-align:center;'>
    <div style='font-size:0.7rem; color:#c9a96e; text-transform:uppercase;
    letter-spacing:1px; margin-bottom:0.8rem;'>A Note on the Technology</div>
    <div style='font-family:Cormorant Garamond,serif; font-style:italic;
    font-size:1rem; color:#c8bfb0; line-height:1.9;'>
    This app uses no proprietary fine-tuning or model retraining.
    Its uniqueness lies entirely in <span style='color:#c9a96e; font-style:normal;'>
    intentional prompt engineering</span> — carefully crafted instructions that direct
    Claude's vast existing knowledge of Vedānta, Sanskrit, and Indian philosophy
    toward precise, reverent, and structured outputs.
    The knowledge was always there. This app simply gives it the right context to serve.
    </div>
</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem;">
    <div style="font-size:1.2rem; letter-spacing:8px;">🪷 🕉️ 🪷</div>
</div>
""", unsafe_allow_html=True)
