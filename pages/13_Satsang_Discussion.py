import streamlit as st
import sys
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="Satsang Discussion Guide · Wisdom Distiller",
    page_icon="🙏",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils.styles import SHARED_CSS
from utils.helpers import make_pdf, make_docx

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
    <h1>🙏 Satsang <span class="accent">Discussion Guide</span></h1>
    <p class="subtitle">For study groups · Chinmaya Mission · Seekers circles</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="about-box">
    Paste any discourse summary or transcript. The AI generates a complete
    <b style='color:#b8a88a;'>satsang facilitation guide</b> — with opening prayers,
    discussion questions at multiple levels of inquiry, group activities, closing
    reflections, and suggested follow-up for the next session.
    Ready to use with your study group or Chinmaya Mission chapter.
</div>
""", unsafe_allow_html=True)

SATSANG_PROMPT = """You are an experienced Vedantic teacher and satsang facilitator,
deeply rooted in the Chinmaya Mission tradition of group study and inquiry.

From the discourse content provided, generate a complete satsang discussion guide.
The guide should serve a group of sincere seekers of mixed levels — from beginners
to advanced students — and should foster genuine inquiry, not mere recall.

CRITICAL: All Sanskrit verses must appear in Devanāgarī script only.

Respond in STRICT JSON ONLY (no markdown fences, no explanation):

{
  "title": "Discussion guide title",
  "scripture": "Scripture reference if applicable",
  "session_duration": "Suggested session duration e.g. 90 minutes",
  "opening_prayer": {
    "verse_devanagari": "Opening verse in Devanāgarī",
    "verse_meaning": "Meaning of the opening verse",
    "invocation_note": "Brief note on why this verse opens the session"
  },
  "session_overview": "2-3 sentence summary of what will be explored in this session",
  "recap_questions": [
    "Simple recall question to ensure everyone has the basic teaching"
  ],
  "beginner_questions": [
    {"question": "Question suitable for new seekers", "purpose": "What this question opens up"}
  ],
  "intermediate_questions": [
    {"question": "Question for seekers with some background", "purpose": "What this question explores"}
  ],
  "deep_inquiry_questions": [
    {"question": "Question for advanced seekers — may have no easy answer", "purpose": "What this question invites"}
  ],
  "group_activity": {
    "title": "Activity name",
    "description": "Description of a group contemplation, sharing, or inquiry activity",
    "duration": "Suggested duration"
  },
  "key_teaching_to_emphasize": "The single most important teaching from this discourse for the group to internalize",
  "common_misconceptions": [
    "A common misunderstanding seekers may have about this teaching, and how to address it"
  ],
  "personal_application": "One concrete way each member can apply this teaching before the next session",
  "closing_reflection": {
    "verse_devanagari": "A closing verse in Devanāgarī",
    "verse_meaning": "Meaning",
    "facilitator_note": "Note for the facilitator on how to close the session"
  },
  "next_session_preview": "Brief pointer to what the group might explore in the next session",
  "resources": [
    "Suggested scripture passage, book, or practice for members to explore before next session"
  ]
}"""


def generate_satsang_guide(content: str, anthropic_key: str) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=anthropic_key)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=SATSANG_PROMPT,
        messages=[{"role": "user", "content": f"Discourse content:\n\n{content}"}]
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    start = raw.find('{')
    end   = raw.rfind('}') + 1
    if start != -1 and end > start:
        raw = raw[start:end]
    return json.loads(raw)


def render_guide(g: dict) -> str:
    export = [
        f"SATSANG DISCUSSION GUIDE: {g.get('title','')}",
        f"Scripture: {g.get('scripture','')} | Duration: {g.get('session_duration','')}",
        ""
    ]

    # Opening
    op = g.get("opening_prayer", {})
    if op:
        st.markdown(f"""
        <div style='background:#0d0d0d;border:1px solid #2a2a2a;border-radius:12px;
        padding:1.4rem 1.8rem;margin-bottom:1.2rem;text-align:center;'>
            <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
            letter-spacing:1px;margin-bottom:0.6rem;'>🪔 Opening Prayer</div>
            <div style='font-family:Cormorant Garamond,serif;font-size:1.4rem;
            color:#c9a96e;line-height:2;margin-bottom:0.6rem;'>
            {op.get('verse_devanagari','')}</div>
            <div style='font-size:0.85rem;color:#888;font-style:italic;'>
            {op.get('verse_meaning','')}</div>
            <div style='font-size:0.78rem;color:#555;margin-top:0.5rem;'>
            {op.get('invocation_note','')}</div>
        </div>
        """, unsafe_allow_html=True)
        export += ["OPENING PRAYER", op.get('verse_devanagari',''),
                   op.get('verse_meaning',''), ""]

    # Overview
    overview = g.get("session_overview","")
    if overview:
        st.markdown(f"""
        <div style='background:#111;border:1px solid #1e1e1e;border-left:3px solid #c9a96e;
        border-radius:10px;padding:1rem 1.3rem;margin-bottom:1.2rem;'>
            <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
            letter-spacing:0.8px;margin-bottom:0.4rem;'>Session Overview</div>
            <div style='font-size:0.9rem;color:#999;line-height:1.8;'>{overview}</div>
        </div>
        """, unsafe_allow_html=True)
        export += ["SESSION OVERVIEW", overview, ""]

    # Discussion Questions
    def render_questions(label, items, color, key_name="question"):
        if not items:
            return
        st.markdown(f"<div class='step-label'>{label}</div>", unsafe_allow_html=True)
        export.append(f"\n{label.upper()}")
        export.append("─"*40)
        for i, item in enumerate(items, 1):
            if isinstance(item, dict):
                q = item.get("question","")
                purpose = item.get("purpose","")
            else:
                q = item
                purpose = ""
            st.markdown(f"""
            <div style='background:#111;border:1px solid #1e1e1e;border-left:3px solid {color};
            border-radius:10px;padding:0.9rem 1.3rem;margin-bottom:0.7rem;'>
                <div style='font-size:0.92rem;color:#e8e0d4;font-weight:500;
                margin-bottom:0.3rem;'>{i}. {q}</div>
                {f"<div style='font-size:0.78rem;color:#555;font-style:italic;'>↳ {purpose}</div>" if purpose else ""}
            </div>
            """, unsafe_allow_html=True)
            export.append(f"{i}. {q}")
            if purpose: export.append(f"   ↳ {purpose}")

    render_questions("Recap — Basic Understanding",
                     g.get("recap_questions",[]), "#888")
    st.markdown("<br/>", unsafe_allow_html=True)
    render_questions("For New Seekers",
                     g.get("beginner_questions",[]), "#a8c88f")
    st.markdown("<br/>", unsafe_allow_html=True)
    render_questions("For Seekers with Background",
                     g.get("intermediate_questions",[]), "#c9a96e")
    st.markdown("<br/>", unsafe_allow_html=True)
    render_questions("Deep Inquiry — For Advanced Seekers",
                     g.get("deep_inquiry_questions",[]), "#8fa8c8")

    # Group Activity
    act = g.get("group_activity",{})
    if act:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:#111;border:1px solid #1e1e1e;border-top:3px solid #c9a96e;
        border-radius:10px;padding:1.1rem 1.4rem;'>
            <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
            letter-spacing:0.8px;margin-bottom:0.4rem;'>
            👥 Group Activity · {act.get('duration','')}</div>
            <div style='font-size:0.92rem;color:#e8e0d4;font-weight:600;
            margin-bottom:0.4rem;'>{act.get('title','')}</div>
            <div style='font-size:0.88rem;color:#999;line-height:1.8;'>
            {act.get('description','')}</div>
        </div>
        """, unsafe_allow_html=True)
        export += ["\nGROUP ACTIVITY", act.get('title',''), act.get('description','')]

    # Key Teaching
    key_t = g.get("key_teaching_to_emphasize","")
    if key_t:
        st.markdown(f"""
        <br/>
        <div style='background:#0d0d0d;border:1px solid #2a2a2a;border-left:4px solid #c9a96e;
        border-radius:10px;padding:1rem 1.4rem;'>
            <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
            letter-spacing:0.8px;margin-bottom:0.5rem;'>⭐ Key Teaching to Emphasize</div>
            <div style='font-family:Cormorant Garamond,serif;font-style:italic;
            font-size:1rem;color:#e8e0d4;line-height:1.9;'>{key_t}</div>
        </div>
        """, unsafe_allow_html=True)
        export += ["\nKEY TEACHING", key_t]

    # Misconceptions
    misc = g.get("common_misconceptions",[])
    if misc:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("<div class='step-label'>Common Misconceptions to Address</div>",
                    unsafe_allow_html=True)
        export.append("\nCOMMON MISCONCEPTIONS")
        for m in misc:
            st.markdown(f"""
            <div style='background:#111;border:1px solid #1e1e1e;border-left:3px solid #c87a6e;
            border-radius:8px;padding:0.7rem 1.2rem;margin-bottom:0.5rem;
            font-size:0.88rem;color:#999;line-height:1.7;'>⚠️ {m}</div>
            """, unsafe_allow_html=True)
            export.append(f"• {m}")

    # Personal Application
    pa = g.get("personal_application","")
    if pa:
        st.markdown(f"""
        <br/>
        <div style='background:#111;border:1px solid #1e1e1e;border-left:3px solid #8fc8c8;
        border-radius:10px;padding:1rem 1.3rem;'>
            <div style='font-size:0.7rem;color:#8fc8c8;text-transform:uppercase;
            letter-spacing:0.8px;margin-bottom:0.4rem;'>🌱 Before Next Session</div>
            <div style='font-size:0.9rem;color:#999;line-height:1.8;'>{pa}</div>
        </div>
        """, unsafe_allow_html=True)
        export += ["\nBEFORE NEXT SESSION", pa]

    # Closing
    cl = g.get("closing_reflection",{})
    if cl:
        st.markdown(f"""
        <br/>
        <div style='background:#0d0d0d;border:1px solid #2a2a2a;border-radius:12px;
        padding:1.4rem 2rem;text-align:center;'>
            <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
            letter-spacing:1px;margin-bottom:0.6rem;'>🪔 Closing Prayer</div>
            <div style='font-family:Cormorant Garamond,serif;font-size:1.4rem;
            color:#c9a96e;line-height:2;margin-bottom:0.5rem;'>
            {cl.get('verse_devanagari','')}</div>
            <div style='font-size:0.85rem;color:#888;font-style:italic;'>
            {cl.get('verse_meaning','')}</div>
            <div style='font-size:0.78rem;color:#555;margin-top:0.5rem;'>
            {cl.get('facilitator_note','')}</div>
        </div>
        """, unsafe_allow_html=True)
        export += ["\nCLOSING", cl.get('verse_devanagari',''), cl.get('verse_meaning','')]

    # Next session + resources
    nxt = g.get("next_session_preview","")
    resources = g.get("resources",[])
    if nxt or resources:
        st.markdown("<br/>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if nxt:
                st.markdown(f"""
                <div style='background:#111;border:1px solid #1e1e1e;border-radius:10px;
                padding:0.9rem 1.2rem;'>
                    <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
                    letter-spacing:0.8px;margin-bottom:0.4rem;'>→ Next Session</div>
                    <div style='font-size:0.85rem;color:#888;line-height:1.7;'>{nxt}</div>
                </div>
                """, unsafe_allow_html=True)
                export += ["\nNEXT SESSION", nxt]
        with col2:
            if resources:
                res_html = "".join(f"<div style='font-size:0.83rem;color:#888;margin-bottom:0.3rem;'>• {r}</div>" for r in resources)
                st.markdown(f"""
                <div style='background:#111;border:1px solid #1e1e1e;border-radius:10px;
                padding:0.9rem 1.2rem;'>
                    <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
                    letter-spacing:0.8px;margin-bottom:0.4rem;'>📚 Resources</div>
                    {res_html}
                </div>
                """, unsafe_allow_html=True)
                export.append("\nRESOURCES")
                export.extend([f"• {r}" for r in resources])

    return "\n".join(export)


# ── Main UI ───────────────────────────────────────────────────────────────────
if not anthropic_key:
    st.warning("⚠️ Please enter your Anthropic API key on the Home page.")
    st.stop()

st.markdown("<div class='step-label'>Step 1 — Provide Discourse Content</div>",
            unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✍️ Paste Text", "📄 Upload .txt"])
source_text = ""
with tab1:
    source_text = st.text_area(
        "Paste content",
        height=200,
        placeholder="Paste any discourse summary, transcript, or notes…",
        key="sdg_paste"
    )
with tab2:
    upl = st.file_uploader("Upload .txt", type=["txt"], key="sdg_upload")
    if upl:
        source_text = upl.read().decode("utf-8", errors="ignore")
        st.success(f"✅ {upl.name} loaded")

st.markdown("<br/>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    group_size = st.selectbox(
        "👥 Group size",
        ["Small (2–5 people)", "Medium (6–15 people)", "Large (15+ people)"],
        key="sdg_size"
    )
with col2:
    level = st.selectbox(
        "📚 Seeker level",
        ["Mixed levels", "Mostly beginners", "Mostly intermediate", "Mostly advanced"],
        key="sdg_level"
    )

st.markdown("<br/>", unsafe_allow_html=True)
if st.button("🙏 Generate Discussion Guide", key="sdg_process", use_container_width=True):
    if not source_text.strip():
        st.error("Please paste or upload discourse content.")
    else:
        enriched = (
            f"[Group size: {group_size} | Level: {level}]\n\n" + source_text
        )
        with st.spinner("Preparing your satsang guide…"):
            try:
                guide = generate_satsang_guide(enriched, anthropic_key)
                st.session_state["sdg_guide"] = guide
            except Exception as e:
                st.error(f"Generation failed: {e}")

if "sdg_guide" in st.session_state:
    guide = st.session_state["sdg_guide"]
    st.markdown("<hr style='border-color:#1e1e1e;margin:1.5rem 0;'/>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='text-align:center;padding:0.5rem 0 1rem;'>
        <div style='font-family:Cormorant Garamond,serif;font-size:1.5rem;
        font-weight:600;color:#e8e0d4;'>{guide.get('title','Satsang Guide')}</div>
        <div style='font-size:0.8rem;color:#555;margin-top:0.2rem;'>
        {guide.get('session_duration','')}
        {'&nbsp;·&nbsp;' + guide.get('scripture','') if guide.get('scripture') else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

    export_text = render_guide(guide)

    # Facilitator notes
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#0d0d0d;border:1px solid #2a2a2a;border-left:3px solid #c9a96e;
    border-radius:10px;padding:1rem 1.4rem;margin-bottom:0.5rem;'>
        <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
        letter-spacing:1px;margin-bottom:0.3rem;'>📝 Facilitator Notes</div>
        <div style='font-size:0.8rem;color:#555;'>
        Add your own preparation notes below. Included in the download.
        </div>
    </div>
    """, unsafe_allow_html=True)
    notes = st.text_area("Facilitator notes", key="sdg_notes", height=100,
                          placeholder="My preparation notes, additional questions, local context…",
                          label_visibility="collapsed")
    if notes.strip():
        export_text += f"\n\nFACILITATOR NOTES\n{'─'*40}\n{notes}"

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div class='step-label'>Export</div>", unsafe_allow_html=True)
    title_str = guide.get("title","Satsang Discussion Guide")
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        st.download_button("📄 TXT", export_text,
                           file_name="satsang_guide.txt", mime="text/plain")
    with dc2:
        try:
            pdf = make_pdf(title_str, export_text,
                           scripture=guide.get("scripture",""))
            st.download_button("📕 PDF", pdf, file_name="satsang_guide.pdf",
                               mime="application/pdf")
        except Exception as e:
            st.caption(f"PDF: {e}")
    with dc3:
        try:
            docx = make_docx(title_str, export_text)
            st.download_button("📘 DOCX", docx, file_name="satsang_guide.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        except Exception as e:
            st.caption(f"DOCX: {e}")

    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🔄 Start over", key="sdg_clear"):
        st.session_state.pop("sdg_guide", None)
        st.rerun()
