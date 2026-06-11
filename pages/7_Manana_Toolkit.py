import streamlit as st
import sys
import csv
import io
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.styles import SHARED_CSS
from utils.helpers import make_pdf, make_docx

st.set_page_config(
    page_title="Manana & Nididhyāsana Toolkit · Wisdom Distiller",
    page_icon="🪷",
    layout="centered"
)
st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    try:
        st.page_link("app.py", label="🏠 Home")
    except Exception:
        if st.button("🏠 Home", key="home_btn_manana"):
            st.switch_page("app.py")
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>",
                unsafe_allow_html=True)

# ── API keys ───────────────────────────────────────────────────────────────────
anthropic_key = st.session_state.get("anthropic_key", "")
if not anthropic_key:
    try:
        anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🪷 Manana &amp; <span class="accent">Nididhyāsana</span> Toolkit</h1>
    <p class="subtitle">From listening to living — tools that help the teaching take root</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="about-box">
    Paste the transcript or summary of any discourse below, then choose a tool.
    Each tool generates a different study aid — from self-testing questions and
    shareable essence cards to a spaced-revision plan and Sanskrit flashcards.
    Use them together for the full arc of <b>Śravaṇa · Manana · Nididhyāsana</b>.
</div>
""", unsafe_allow_html=True)

# ── Discourse input ────────────────────────────────────────────────────────────
st.markdown('<div class="step-label">Step 1 — Paste Your Discourse Text</div>',
            unsafe_allow_html=True)
st.markdown(
    "<div style='font-size:0.83rem;color:#888;margin-bottom:0.5rem;'>"
    "Paste a transcript or summary you've already generated — "
    "from the Audio Summarizer, Discourse Transcriber, or any other source."
    "</div>",
    unsafe_allow_html=True
)
discourse_text = st.text_area(
    "Discourse text",
    height=220,
    placeholder=(
        "Paste the discourse transcript or summary here...\n\n"
        "You can use the output from the Audio Summarizer or "
        "Discourse Transcriber pages directly."
    ),
    label_visibility="collapsed"
)

dc1, dc2 = st.columns(2)
with dc1:
    speaker = st.text_input("🎙️ Speaker (optional)",
                             placeholder="e.g. Swami Tejomayananda",
                             key="mn_speaker")
with dc2:
    scripture = st.text_input("📚 Scripture / Topic (optional)",
                               placeholder="e.g. Bhagavad Gītā Ch. 2",
                               key="mn_scripture")

st.markdown("---")

# ── Tool cards ─────────────────────────────────────────────────────────────────
st.markdown('<div class="step-label">Step 2 — Choose a Tool</div>',
            unsafe_allow_html=True)

st.markdown("""
<style>
.tool-card {
    background: #111;
    border: 1px solid #2a2a2a;
    border-top: 3px solid #c9a96e;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
    min-height: 155px;
    margin-bottom: 0.2rem;
}
.tool-icon  { font-size: 1.9rem; margin-bottom: 0.35rem; }
.tool-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.05rem;
    color: #e8e0d4;
    margin-bottom: 0.3rem;
}
.tool-desc  { font-size: 0.76rem; color: #888; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# Row 1
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-icon">❓</div>
        <div class="tool-title">Praśna Mañjarī</div>
        <div class="tool-desc">Questions This Discourse Answers<br/>
        5–8 Manana prompts for self-testing &amp; group discussion</div>
    </div>""", unsafe_allow_html=True)
    run_prashna = st.button("❓ Generate Questions",
                             key="btn_prashna", use_container_width=True)

with col2:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-icon">✨</div>
        <div class="tool-title">Sārāmṛta Card</div>
        <div class="tool-desc">One-Card Distillation<br/>
        One sentence · one verse · one practice — ready to share</div>
    </div>""", unsafe_allow_html=True)
    run_saramrita = st.button("✨ Generate Essence Card",
                               key="btn_saramrita", use_container_width=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Row 2
col3, col4 = st.columns(2)
with col3:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-icon">📅</div>
        <div class="tool-title">Punarāvṛtti Sheet</div>
        <div class="tool-desc">Spaced Revision Plan<br/>
        Tomorrow · This week · This month — wisdom absorbed in layers</div>
    </div>""", unsafe_allow_html=True)
    run_punar = st.button("📅 Generate Revision Plan",
                           key="btn_punar", use_container_width=True)

with col4:
    st.markdown("""
    <div class="tool-card">
        <div class="tool-icon">🃏</div>
        <div class="tool-title">Pada Kośa Cards</div>
        <div class="tool-desc">Sanskrit Flashcard Export<br/>
        Term · meaning · context — export as CSV (Anki-ready) or PDF</div>
    </div>""", unsafe_allow_html=True)
    run_pada = st.button("🃏 Generate Flashcards",
                          key="btn_pada", use_container_width=True)

st.markdown("---")


# ── Shared guard ───────────────────────────────────────────────────────────────
def _guard():
    if not discourse_text.strip():
        st.warning("⚠️ Please paste your discourse text in Step 1 above.")
        return False
    if not anthropic_key:
        st.warning("⚠️ Please enter your Anthropic API key in the sidebar.")
        return False
    return True


def _call_claude(prompt: str, max_tokens: int = 2000) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=anthropic_key)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text


def _header_meta():
    parts = []
    if speaker:
        parts.append(f"Speaker: {speaker}")
    if scripture:
        parts.append(f"Scripture / Topic: {scripture}")
    return "  |  ".join(parts) if parts else ""


# ── TOOL 1 — Praśna Mañjarī ───────────────────────────────────────────────────
if run_prashna:
    if _guard():
        with st.spinner("Generating Manana questions…"):
            meta = _header_meta()
            prompt = (
                f"You are an expert in Vedantic teaching.\n"
                f"{('Context — ' + meta + chr(10)) if meta else ''}"
                f"Read the following discourse carefully.\n\n"
                f"Generate exactly 7 questions that this discourse implicitly answers. "
                f"These are Manana prompts — questions a sincere seeker would sit with "
                f"after hearing this talk. Each question should:\n"
                f"- Be self-contained and meaningful even without the transcript\n"
                f"- Arise naturally from the teaching (not trivial recall)\n"
                f"- Be phrased as a genuine inquiry, not a test question\n\n"
                f"Format: numbered list, one question per line, no extra commentary.\n\n"
                f"DISCOURSE:\n{discourse_text}"
            )
            try:
                result = _call_claude(prompt, max_tokens=800)
                st.session_state["mn_prashna"] = result
            except Exception as e:
                st.error(f"❌ {e}")

if "mn_prashna" in st.session_state:
    st.markdown("""
    <div style='background:#0d0d0d;border:1px solid #2a2a2a;
    border-left:3px solid #c9a96e;border-radius:10px;padding:1.2rem 1.5rem;'>
    <div style='font-family:Cormorant Garamond,serif;font-size:1.1rem;
    color:#c9a96e;font-weight:600;margin-bottom:0.8rem;'>
    ❓ Praśna Mañjarī — Questions This Discourse Answers</div>
    """, unsafe_allow_html=True)
    st.markdown(st.session_state["mn_prashna"])
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    _title = f"Praśna Mañjarī{(' — ' + speaker) if speaker else ''}"
    with c1:
        st.download_button("⬇️ PDF", key="dl_prashna_pdf",
            data=make_pdf(_title, st.session_state["mn_prashna"]),
            file_name="prashna_manjari.pdf", mime="application/pdf")
    with c2:
        st.download_button("⬇️ TXT", key="dl_prashna_txt",
            data=st.session_state["mn_prashna"],
            file_name="prashna_manjari.txt", mime="text/plain")
    st.markdown("---")


# ── TOOL 2 — Sārāmṛta Card ────────────────────────────────────────────────────
if run_saramrita:
    if _guard():
        with st.spinner("Distilling the essence…"):
            meta = _header_meta()
            prompt = (
                f"You are an expert in Vedantic teaching.\n"
                f"{('Context — ' + meta + chr(10)) if meta else ''}"
                f"Read the following discourse and create a Sārāmṛta Card — "
                f"a single shareable essence card with exactly three elements:\n\n"
                f"1. ESSENCE (one sentence): The single most important teaching of this "
                f"discourse in plain, beautiful English. No jargon. A non-Vedantin should "
                f"understand it immediately.\n\n"
                f"2. VERSE (one key verse or teaching-line): The most central Sanskrit "
                f"verse or aphorism from this discourse. Present it in Devanāgarī script "
                f"followed by its English meaning on the next line. If no verse was "
                f"quoted, choose the most quotable statement made.\n\n"
                f"3. PRACTICE (one thing to do today): A single, concrete, actionable "
                f"practice to carry this teaching into daily life — one sentence.\n\n"
                f"Format your response with exactly these three bold headings:\n"
                f"**✨ Essence**\n**📿 Verse**\n**🌿 Practice**\n\n"
                f"DISCOURSE:\n{discourse_text}"
            )
            try:
                result = _call_claude(prompt, max_tokens=600)
                st.session_state["mn_saramrita"] = result
            except Exception as e:
                st.error(f"❌ {e}")

if "mn_saramrita" in st.session_state:
    st.markdown("""
    <div style='background:#0d0d0d;border:1px solid #2a2a2a;
    border-left:3px solid #c9a96e;border-radius:10px;padding:1.4rem 1.8rem;
    max-width:560px;margin:0 auto;'>
    <div style='font-family:Cormorant Garamond,serif;font-size:1.1rem;
    color:#c9a96e;font-weight:600;margin-bottom:0.8rem;text-align:center;'>
    ✨ Sārāmṛta Card</div>
    """, unsafe_allow_html=True)
    if speaker or scripture:
        st.markdown(
            f"<div style='text-align:center;font-size:0.75rem;color:#555;"
            f"margin-bottom:0.8rem;'>{_header_meta()}</div>",
            unsafe_allow_html=True
        )
    st.markdown(st.session_state["mn_saramrita"])
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    _title = f"Sārāmṛta Card{(' — ' + speaker) if speaker else ''}"
    with c1:
        st.download_button("⬇️ PDF", key="dl_saramrita_pdf",
            data=make_pdf(_title, st.session_state["mn_saramrita"]),
            file_name="saramrita_card.pdf", mime="application/pdf")
    with c2:
        st.download_button("⬇️ DOCX", key="dl_saramrita_docx",
            data=make_docx(_title, st.session_state["mn_saramrita"]),
            file_name="saramrita_card.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    with c3:
        st.download_button("⬇️ TXT", key="dl_saramrita_txt",
            data=st.session_state["mn_saramrita"],
            file_name="saramrita_card.txt", mime="text/plain")
    st.markdown("---")


# ── TOOL 3 — Punarāvṛtti Sheet ───────────────────────────────────────────────
if run_punar:
    if _guard():
        with st.spinner("Building your revision plan…"):
            meta = _header_meta()
            prompt = (
                f"You are an expert in Vedantic teaching and spaced learning.\n"
                f"{('Context — ' + meta + chr(10)) if meta else ''}"
                f"Read the following discourse and create a Punarāvṛtti (Spaced Revision) "
                f"Sheet with three tiers:\n\n"
                f"**📌 TOMORROW — 3 Points to Recall**\n"
                f"The 3 most important teachings to hold in mind tomorrow. "
                f"Short, crisp bullets — each one sentence.\n\n"
                f"**🌙 THIS WEEK — One Question to Sit With**\n"
                f"A single deep Manana question to contemplate over the coming week. "
                f"It should open inquiry rather than demand a quick answer.\n\n"
                f"**🌕 THIS MONTH — Core Verse to Recite**\n"
                f"The single most important Sanskrit verse or teaching-line from this "
                f"discourse to memorize and recite daily for the next month. "
                f"Present it in Devanāgarī, then its transliteration, then its meaning. "
                f"If no verse was quoted, choose the most central teaching-line.\n\n"
                f"Use exactly these three bold headings. Keep each section brief and "
                f"actionable — this is a practice sheet, not an essay.\n\n"
                f"DISCOURSE:\n{discourse_text}"
            )
            try:
                result = _call_claude(prompt, max_tokens=800)
                st.session_state["mn_punar"] = result
            except Exception as e:
                st.error(f"❌ {e}")

if "mn_punar" in st.session_state:
    st.markdown("""
    <div style='background:#0d0d0d;border:1px solid #2a2a2a;
    border-left:3px solid #c9a96e;border-radius:10px;padding:1.2rem 1.5rem;'>
    <div style='font-family:Cormorant Garamond,serif;font-size:1.1rem;
    color:#c9a96e;font-weight:600;margin-bottom:0.8rem;'>
    📅 Punarāvṛtti Sheet — Spaced Revision Plan</div>
    """, unsafe_allow_html=True)
    st.markdown(st.session_state["mn_punar"])
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    _title = f"Punarāvṛtti Sheet{(' — ' + speaker) if speaker else ''}"
    with c1:
        st.download_button("⬇️ PDF", key="dl_punar_pdf",
            data=make_pdf(_title, st.session_state["mn_punar"]),
            file_name="punaravrutti_sheet.pdf", mime="application/pdf")
    with c2:
        st.download_button("⬇️ DOCX", key="dl_punar_docx",
            data=make_docx(_title, st.session_state["mn_punar"]),
            file_name="punaravrutti_sheet.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    with c3:
        st.download_button("⬇️ TXT", key="dl_punar_txt",
            data=st.session_state["mn_punar"],
            file_name="punaravrutti_sheet.txt", mime="text/plain")
    st.markdown("---")


# ── TOOL 4 — Pada Kośa Cards ──────────────────────────────────────────────────
if run_pada:
    if _guard():
        with st.spinner("Extracting Sanskrit flashcards…"):
            meta = _header_meta()
            prompt = (
                f"You are an expert in Sanskrit and Vedantic teaching.\n"
                f"{('Context — ' + meta + chr(10)) if meta else ''}"
                f"Read the following discourse and extract every important Sanskrit term "
                f"mentioned or implied.\n\n"
                f"For each term, provide exactly these four fields:\n"
                f"TERM: The Sanskrit word (in Devanāgarī script)\n"
                f"TRANSLITERATION: Roman transliteration with diacritics\n"
                f"MEANING: Clear English meaning (1–2 sentences)\n"
                f"CONTEXT: The exact sentence or phrase from the discourse where "
                f"the speaker used or explained this term (quote it directly if possible; "
                f"otherwise paraphrase closely)\n\n"
                f"Separate each term with a blank line. "
                f"Include at least 8 terms and up to 20. "
                f"Only include terms that genuinely appeared in this discourse — "
                f"do not invent terms.\n\n"
                f"DISCOURSE:\n{discourse_text}"
            )
            try:
                raw = _call_claude(prompt, max_tokens=2500)
                st.session_state["mn_pada_raw"] = raw

                # Parse into structured list for CSV
                cards = []
                current = {}
                for line in raw.split("\n"):
                    line = line.strip()
                    if line.startswith("TERM:"):
                        if current:
                            cards.append(current)
                        current = {"term": line[5:].strip(), "transliteration": "",
                                   "meaning": "", "context": ""}
                    elif line.startswith("TRANSLITERATION:"):
                        current["transliteration"] = line[16:].strip()
                    elif line.startswith("MEANING:"):
                        current["meaning"] = line[8:].strip()
                    elif line.startswith("CONTEXT:"):
                        current["context"] = line[8:].strip()
                if current and current.get("term"):
                    cards.append(current)
                st.session_state["mn_pada_cards"] = cards
            except Exception as e:
                st.error(f"❌ {e}")

if "mn_pada_raw" in st.session_state:
    cards = st.session_state.get("mn_pada_cards", [])
    st.markdown("""
    <div style='background:#0d0d0d;border:1px solid #2a2a2a;
    border-left:3px solid #c9a96e;border-radius:10px;padding:1.2rem 1.5rem;'>
    <div style='font-family:Cormorant Garamond,serif;font-size:1.1rem;
    color:#c9a96e;font-weight:600;margin-bottom:1rem;'>
    🃏 Pada Kośa Cards — Sanskrit Flashcards</div>
    """, unsafe_allow_html=True)

    # Render each card as a small pill-card
    for card in cards:
        st.markdown(
            f"<div style='background:#161616;border:1px solid #2a2a2a;"
            f"border-radius:8px;padding:0.8rem 1.1rem;margin-bottom:0.6rem;'>"
            f"<div style='font-size:1.1rem;color:#e8e0d4;font-family:serif;"
            f"margin-bottom:0.15rem;'>{card.get('term','')}"
            f" <span style='font-size:0.8rem;color:#666;font-family:sans-serif;'>"
            f"{card.get('transliteration','')}</span></div>"
            f"<div style='font-size:0.82rem;color:#c9a96e;margin-bottom:0.2rem;'>"
            f"{card.get('meaning','')}</div>"
            f"<div style='font-size:0.75rem;color:#555;font-style:italic;'>"
            f"&ldquo;{card.get('context','')}&rdquo;</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # CSV export (Anki-compatible: front, back)
    if cards:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Front (Sanskrit)", "Transliteration",
                         "Back (Meaning)", "Context"])
        for card in cards:
            writer.writerow([card.get("term", ""), card.get("transliteration", ""),
                             card.get("meaning", ""), card.get("context", "")])
        csv_bytes = buf.getvalue().encode("utf-8")

    _title = f"Pada Kośa Cards{(' — ' + speaker) if speaker else ''}"
    c1, c2, c3 = st.columns(3)
    with c1:
        if cards:
            st.download_button("⬇️ CSV (Anki)", key="dl_pada_csv",
                data=csv_bytes,
                file_name="pada_kosa_cards.csv", mime="text/csv")
    with c2:
        st.download_button("⬇️ PDF", key="dl_pada_pdf",
            data=make_pdf(_title, st.session_state["mn_pada_raw"]),
            file_name="pada_kosa_cards.pdf", mime="application/pdf")
    with c3:
        st.download_button("⬇️ TXT", key="dl_pada_txt",
            data=st.session_state["mn_pada_raw"],
            file_name="pada_kosa_cards.txt", mime="text/plain")
    st.markdown("---")


# ── Footer quote ───────────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;padding:1.5rem 1rem 2rem;'>"
    "<div style='font-family:Cormorant Garamond,serif;font-style:italic;"
    "font-size:1.05rem;color:#c9a96e;line-height:1.9;max-width:480px;margin:0 auto;'>"
    "śravaṇaṃ kīrtanaṃ viṣṇoḥ smaraṇaṃ pāda-sevanam —<br/>"
    "<span style='font-size:0.82rem;color:#666;font-style:normal;'>"
    "Listening · Reflecting · Remembering · Serving</span>"
    "</div></div>",
    unsafe_allow_html=True
)
