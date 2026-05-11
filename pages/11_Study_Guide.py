import streamlit as st
import sys
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="Study Guide · Wisdom Distiller",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils.styles import SHARED_CSS
from utils.helpers import make_pdf, make_docx, LANGUAGES

st.markdown(SHARED_CSS, unsafe_allow_html=True)

with st.sidebar:
    try:
        st.page_link("app.py", label="🏠 Home")
    except Exception:
        pass
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>",
                unsafe_allow_html=True)

anthropic_key = st.session_state.get("anthropic_key", "")
if not anthropic_key:
    try: anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
    except: pass

st.markdown("""
<div class="hero">
    <h1>📖 Study <span class="accent">Guide Generator</span></h1>
    <p class="subtitle">Deepen your understanding · Manana & Nididhyāsana</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="about-box">
    Paste a discourse summary or transcript and receive a complete
    <b style='color:#b8a88a;'>structured study guide</b> — with key concepts, contemplation
    questions, practical applications, a 7-day reflection plan, and further scriptural
    references. Designed to support the full arc of Vedantic learning.
</div>
""", unsafe_allow_html=True)

STUDY_PROMPT = """You are a senior Vedantic teacher and scholar, deeply familiar with
Advaita Vedānta, the Upaniṣads, Bhagavad Gītā, and the Chinmaya Mission tradition.

From the discourse content provided, generate a complete, structured study guide for a
sincere seeker. The guide should support all three stages of Vedantic learning:
Śravaṇa (hearing), Manana (reflection), and Nididhyāsana (deep contemplation).

CRITICAL SANSKRIT RULE: All Sanskrit verses must appear in Devanāgarī script only.
Never transliterate verses into Roman script. Sanskrit terms may include transliteration
in parentheses for clarity.

Generate the study guide in this EXACT JSON format (no markdown fences, no preamble):

{
  "title": "Study Guide title based on discourse topic",
  "speaker": "Speaker name if mentioned",
  "scripture": "Scripture reference if mentioned",
  "essence": "2-3 sentence core teaching of this discourse",
  "key_concepts": [
    {"term": "Sanskrit term or concept", "devanagari": "Devanāgarī if applicable", "meaning": "Clear explanation in 2-3 sentences"}
  ],
  "contemplation_questions": [
    {"question": "Deep question for manana", "hint": "A gentle pointer to guide reflection"}
  ],
  "practical_applications": [
    "Specific practice or application the seeker can implement in daily life"
  ],
  "scriptural_references": [
    {"reference": "Scripture Name Chapter.Verse", "devanagari": "Verse in Devanāgarī", "meaning": "Meaning of this verse"}
  ],
  "seven_day_plan": [
    {"day": 1, "theme": "Theme for the day", "practice": "Specific contemplation or practice for this day"}
  ],
  "closing_teaching": "A final inspiring sentence from the tradition that encapsulates this discourse"
}"""


def generate_study_guide(content: str, anthropic_key: str) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=anthropic_key)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=STUDY_PROMPT,
        messages=[{"role": "user", "content": f"Discourse content:\n\n{content}"}]
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    # Extract JSON block
    start = raw.find('{')
    end   = raw.rfind('}') + 1
    if start != -1 and end > start:
        raw = raw[start:end]
    return json.loads(raw)


def render_study_guide(g: dict) -> str:
    """Render guide and return export text."""
    # ── Essence ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:#0d0d0d;border:1px solid #2a2a2a;border-left:4px solid #c9a96e;
    border-radius:12px;padding:1.4rem 1.8rem;margin-bottom:1.5rem;text-align:center;'>
        <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
        letter-spacing:1px;margin-bottom:0.6rem;'>✦ Core Teaching</div>
        <div style='font-family:Cormorant Garamond,serif;font-style:italic;
        font-size:1.05rem;color:#e8e0d4;line-height:1.9;'>{g.get("essence","")}</div>
    </div>
    """, unsafe_allow_html=True)

    export_lines = [
        f"STUDY GUIDE: {g.get('title','')}",
        f"Speaker: {g.get('speaker','')} | Scripture: {g.get('scripture','')}",
        "", "CORE TEACHING", "─"*40,
        g.get("essence",""), ""
    ]

    # ── Key Concepts ──────────────────────────────────────────────────────────
    st.markdown("<div class='step-label'>Key Concepts</div>", unsafe_allow_html=True)
    export_lines += ["KEY CONCEPTS", "─"*40]
    for kc in g.get("key_concepts", []):
        deva = f" {kc.get('devanagari','')}" if kc.get('devanagari') else ""
        st.markdown(f"""
        <div style='background:#111;border:1px solid #1e1e1e;border-left:3px solid #c9a96e;
        border-radius:10px;padding:0.9rem 1.3rem;margin-bottom:0.7rem;'>
            <div style='font-size:0.95rem;font-weight:600;color:#c9a96e;margin-bottom:0.3rem;'>
                {kc.get('term','')}<span style='font-size:1rem;margin-left:0.5rem;'>{deva}</span>
            </div>
            <div style='font-size:0.88rem;color:#999;line-height:1.8;'>{kc.get('meaning','')}</div>
        </div>
        """, unsafe_allow_html=True)
        export_lines.append(f"\n{kc.get('term','')} {deva}\n{kc.get('meaning','')}")
    export_lines.append("")

    # ── Contemplation Questions ───────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div class='step-label'>Contemplation Questions — Manana</div>",
                unsafe_allow_html=True)
    export_lines += ["CONTEMPLATION QUESTIONS", "─"*40]
    for i, cq in enumerate(g.get("contemplation_questions", []), 1):
        st.markdown(f"""
        <div style='background:#111;border:1px solid #1e1e1e;border-radius:10px;
        padding:1rem 1.3rem;margin-bottom:0.7rem;'>
            <div style='font-size:0.92rem;color:#e8e0d4;font-weight:500;margin-bottom:0.4rem;'>
                {i}. {cq.get('question','')}
            </div>
            <div style='font-size:0.82rem;color:#555;font-style:italic;'>
                💡 {cq.get('hint','')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        export_lines.append(f"\n{i}. {cq.get('question','')}\n   Hint: {cq.get('hint','')}")
    export_lines.append("")

    # ── Practical Applications ────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div class='step-label'>Practical Applications</div>", unsafe_allow_html=True)
    export_lines += ["PRACTICAL APPLICATIONS", "─"*40]
    for app in g.get("practical_applications", []):
        st.markdown(f"""
        <div style='background:#111;border:1px solid #1e1e1e;border-left:3px solid #8fc8c8;
        border-radius:8px;padding:0.7rem 1.2rem;margin-bottom:0.5rem;
        font-size:0.88rem;color:#999;line-height:1.7;'>• {app}</div>
        """, unsafe_allow_html=True)
        export_lines.append(f"• {app}")
    export_lines.append("")

    # ── Scriptural References ─────────────────────────────────────────────────
    refs = g.get("scriptural_references", [])
    if refs:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("<div class='step-label'>Scriptural References</div>",
                    unsafe_allow_html=True)
        export_lines += ["SCRIPTURAL REFERENCES", "─"*40]
        for ref in refs:
            deva = ref.get('devanagari','')
            st.markdown(f"""
            <div style='background:#111;border:1px solid #1e1e1e;border-radius:10px;
            padding:1rem 1.3rem;margin-bottom:0.7rem;'>
                <div style='font-size:0.8rem;color:#c9a96e;font-weight:600;
                margin-bottom:0.4rem;'>{ref.get('reference','')}</div>
                {f"<div style='font-size:1.1rem;color:#c9a96e;margin-bottom:0.4rem;'>{deva}</div>" if deva else ""}
                <div style='font-size:0.88rem;color:#999;line-height:1.7;'>{ref.get('meaning','')}</div>
            </div>
            """, unsafe_allow_html=True)
            export_lines.append(f"\n{ref.get('reference','')}")
            if deva: export_lines.append(deva)
            export_lines.append(ref.get('meaning',''))
        export_lines.append("")

    # ── 7-Day Plan ────────────────────────────────────────────────────────────
    plan = g.get("seven_day_plan", [])
    if plan:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("<div class='step-label'>7-Day Reflection Plan</div>",
                    unsafe_allow_html=True)
        export_lines += ["7-DAY REFLECTION PLAN", "─"*40]
        cols = st.columns(7)
        days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        for i, day_item in enumerate(plan[:7]):
            with cols[i]:
                st.markdown(f"""
                <div style='background:#111;border:1px solid #2a2a2a;border-top:3px solid #c9a96e;
                border-radius:8px;padding:0.7rem 0.5rem;text-align:center;min-height:140px;'>
                    <div style='font-size:0.65rem;color:#c9a96e;text-transform:uppercase;
                    letter-spacing:0.5px;'>Day {day_item.get('day',i+1)}</div>
                    <div style='font-size:0.7rem;color:#e8e0d4;font-weight:600;
                    margin:0.3rem 0;line-height:1.3;'>{day_item.get('theme','')}</div>
                    <div style='font-size:0.68rem;color:#666;line-height:1.4;'>
                    {day_item.get('practice','')}</div>
                </div>
                """, unsafe_allow_html=True)
            export_lines.append(
                f"Day {day_item.get('day',i+1)} — {day_item.get('theme','')}: "
                f"{day_item.get('practice','')}"
            )
        export_lines.append("")

    # ── Closing Teaching ──────────────────────────────────────────────────────
    closing = g.get("closing_teaching","")
    if closing:
        st.markdown(f"""
        <br/>
        <div style='background:#0d0d0d;border:1px solid #1e1e1e;border-radius:12px;
        padding:1.4rem 2rem;text-align:center;margin-top:1rem;'>
            <div style='font-family:Cormorant Garamond,serif;font-style:italic;
            font-size:1.05rem;color:#c9a96e;line-height:1.9;'>"{closing}"</div>
        </div>
        """, unsafe_allow_html=True)
        export_lines += ["", "CLOSING TEACHING", "─"*40, f'"{closing}"']

    return "\n".join(export_lines)


# ── UI ────────────────────────────────────────────────────────────────────────
if not anthropic_key:
    st.warning("⚠️ Please enter your Anthropic API key on the Home page.")
    st.stop()

st.markdown("<div class='step-label'>Step 1 — Provide Discourse Content</div>",
            unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✍️ Paste Text", "📄 Upload .txt"])
source_text = ""

with tab1:
    source_text = st.text_area(
        "Paste summary or transcript",
        height=220,
        placeholder="Paste any discourse summary, transcript, or notes here…",
        key="sg_paste"
    )
with tab2:
    upl = st.file_uploader("Upload .txt file", type=["txt"], key="sg_upload")
    if upl:
        source_text = upl.read().decode("utf-8", errors="ignore")
        st.success(f"✅ {upl.name} loaded ({len(source_text):,} characters)")

st.markdown("<br/>", unsafe_allow_html=True)
if st.button("📖 Generate Study Guide", key="sg_process", use_container_width=True):
    if not source_text.strip():
        st.error("Please paste or upload discourse content first.")
    else:
        with st.spinner("Crafting your study guide…"):
            try:
                guide = generate_study_guide(source_text, anthropic_key)
                st.session_state["sg_guide"]  = guide
                st.session_state["sg_source"] = source_text
            except Exception as e:
                st.error(f"Generation failed: {e}")

if "sg_guide" in st.session_state:
    guide = st.session_state["sg_guide"]
    st.markdown("<hr style='border-color:#1e1e1e;margin:1.5rem 0;'/>", unsafe_allow_html=True)

    # Header
    st.markdown(f"""
    <div style='text-align:center;padding:0.5rem 0 1rem;'>
        <div style='font-family:Cormorant Garamond,serif;font-size:1.5rem;
        font-weight:600;color:#e8e0d4;'>{guide.get('title','Study Guide')}</div>
        <div style='font-size:0.8rem;color:#555;margin-top:0.3rem;'>
        {guide.get('speaker','')}
        {'&nbsp;·&nbsp;' + guide.get('scripture','') if guide.get('scripture') else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

    export_text = render_study_guide(guide)

    # Reflection
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#0d0d0d;border:1px solid #2a2a2a;border-left:3px solid #c9a96e;
    border-radius:10px;padding:1rem 1.4rem;margin-bottom:0.5rem;'>
        <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
        letter-spacing:1px;margin-bottom:0.3rem;'>🪷 My Reflections</div>
        <div style='font-size:0.8rem;color:#555;'>Your notes will be included in the download.</div>
    </div>
    """, unsafe_allow_html=True)
    reflection = st.text_area("Reflections", key="sg_reflection", height=120,
                               placeholder="My thoughts, questions, insights…",
                               label_visibility="collapsed")
    if reflection.strip():
        export_text += f"\n\nMY REFLECTIONS\n{'─'*40}\n{reflection}"

    # Downloads
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div class='step-label'>Export</div>", unsafe_allow_html=True)
    title_str = guide.get("title", "Study Guide")
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        st.download_button("📄 TXT", export_text,
                           file_name="study_guide.txt", mime="text/plain")
    with dc2:
        try:
            pdf = make_pdf(title_str, export_text,
                           speaker=guide.get("speaker",""),
                           scripture=guide.get("scripture",""))
            st.download_button("📕 PDF", pdf, file_name="study_guide.pdf",
                               mime="application/pdf")
        except Exception as e:
            st.caption(f"PDF: {e}")
    with dc3:
        try:
            docx = make_docx(title_str, export_text)
            st.download_button("📘 DOCX", docx, file_name="study_guide.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        except Exception as e:
            st.caption(f"DOCX: {e}")

    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🔄 Start over", key="sg_clear"):
        for k in ["sg_guide", "sg_source"]:
            st.session_state.pop(k, None)
        st.rerun()
