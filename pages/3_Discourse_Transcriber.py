import streamlit as st
import sys
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="Discourse Transcriber · Wisdom Distiller",
    page_icon="📜",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils.styles import SHARED_CSS
from utils.helpers import (
    prepare_audio_chunks,
    transcribe_chunks,
    summarize_text,
    structure_transcript,
    translate_text,
    make_pdf, make_docx, LANGUAGES
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)

with st.sidebar:
    try:
        st.page_link("app.py", label="🏠 Home")
    except Exception:
        pass
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>", unsafe_allow_html=True)

anthropic_key = st.session_state.get("anthropic_key", "")
openai_key    = st.session_state.get("openai_key", "")
if not anthropic_key:
    try: anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
    except: pass
if not openai_key:
    try: openai_key = st.secrets["OPENAI_API_KEY"]
    except: pass

st.markdown("""
<div class="hero">
    <h1>📜 Discourse <span class="accent">Transcriber</span></h1>
    <p class="subtitle">Transcribe · Structure · Preserve · Export</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="about-box">
    Upload a discourse audio file. The AI transcribes it and produces a
    <b style='color:#b8a88a;'>polished, structured transcript</b> with section headings,
    Sanskrit verses in <b style='color:#c9a96e;'>Devanāgarī script</b>, and a summary.
</div>
""", unsafe_allow_html=True)

SPEAKERS = ["Swāmī Aparājitānandajī", "Swāmī Śaraṇānandajī", "Other / Not specified"]
SCRIPTURES = [
    "Bhagavad Gītā", "Upaniṣads", "Vivekachūḍāmaṇi", "Tattva Bodha",
    "Bhaja Govindam", "Soundarya Laharī", "Kaṭhopaniṣad",
    "Māṇḍūkya Upaniṣad", "Muṇḍaka Upaniṣad", "Yoga Vāsiṣṭha",
    "Srimad Bhāgavatam", "Rāmāyaṇa / Sundara Kāṇḍa", "Other / Not specified",
]

# ── Step 1 ────────────────────────────────────────────────────────────────────
st.markdown("<div class='step-label'>Step 1 — Discourse Details</div>", unsafe_allow_html=True)
d1, d2 = st.columns(2)
with d1:
    speaker = st.selectbox("🎙️ Speaker", SPEAKERS, key="dt_speaker")
    if speaker == "Other / Not specified":
        speaker = st.text_input("Enter speaker name", key="dt_speaker_other",
                                placeholder="e.g. Swāmī Tejomayānandajī")
with d2:
    topic = st.text_input("📖 Topic / Title", key="dt_topic",
                          placeholder="e.g. Introduction to Vivekachūḍāmaṇi")

d3, d4, d5 = st.columns(3)
with d3:
    scripture = st.selectbox("📚 Scripture", SCRIPTURES, key="dt_scripture")
    if scripture == "Other / Not specified":
        scripture = st.text_input("Enter scripture", key="dt_scripture_other")
with d4:
    chapter = st.text_input("📑 Chapter / Discourse", key="dt_chapter", placeholder="e.g. Chapter 2, Day 3, Session 1")
with d5:
    verse_range = st.text_input("📿 Verse Range (optional)", key="dt_verse",
                                placeholder="e.g. Verses 3–7, Mantra 5")

output_lang = st.selectbox("🌐 Output Language", list(LANGUAGES.keys()), key="dt_lang")

# ── Custom Focus Prompt ────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<div class='step-label'>Additional Focus / Custom Prompt (optional)</div>",
            unsafe_allow_html=True)
st.markdown(
    "<div style='font-size:0.82rem;color:#666;margin-bottom:0.5rem;'>"
    "Add specific instructions for the AI — e.g. highlight areas Swamiji stressed, "
    "identify cross-scriptural references, flag analogies used, mark Q&amp;A sections, etc."
    "</div>",
    unsafe_allow_html=True
)
# ── Preset examples organised by category ────────────────────────────────────
FOCUS_PRESETS = {
    "— Select a preset to add —": "",
    # Emphasis & Stress
    "📌 Highlight repeated/stressed points": "Highlight every place where Swamiji has repeated or strongly stressed a point.",
    "📌 Mark 'remember this' moments": "Flag any place where Swamiji says 'remember this', 'this is very important', or similar emphasis.",
    "📌 Note changes in tone or pace": "Mark statements where the teacher's tone, pace, or voice indicates special importance.",
    # Cross-references
    "📚 All cross-scripture references": "Identify every place where another scripture is referenced or quoted, and name the scripture.",
    "📚 Upaniṣadic mahāvākyas": "Note all Upaniṣadic mahāvākyas mentioned, their Devanāgarī, and their source Upaniṣad.",
    "📚 Bhagavatam references": "Flag all Srimad Bhāgavatam references or stories used as illustrations.",
    "📚 Rāmāyaṇa / Mahābhārata references": "Flag all Rāmāyaṇa or Mahābhārata references used as illustrations.",
    "📚 Bhagavad Gītā verses cited": "Identify every Bhagavad Gītā verse quoted, with chapter and verse number.",
    # Teaching style
    "🎭 All analogies and stories": "Flag all analogies, stories, and examples used to explain concepts. Label each with [ANALOGY] or [STORY].",
    "🎭 Rhetorical questions": "Mark all rhetorical questions the teacher poses to the audience.",
    "🎭 Practical sādhana instructions": "Identify every place where the teacher gives a practical instruction, practice, or sādhana for the seeker.",
    "🎭 Humour and lightness": "Note any moments of humour, lightness, or wit used to illustrate a point.",
    # Sanskrit study
    "🕉️ All Sanskrit terms with meanings": "Mark all Sanskrit terms, provide Devanāgarī script and meaning for each.",
    "🕉️ Every shloka with source": "Identify every shloka or mantra quoted, give it in Devanāgarī, and note its source scripture.",
    "🕉️ Technical Vedantic terms explained": "Flag all technical Advaita Vedānta terms and briefly explain each in simple language.",
    "🕉️ Sanskrit etymology highlights": "Where the teacher breaks down a Sanskrit word etymologically, highlight that explanation.",
    # Specific themes
    "🧠 Mind — manas/buddhi/ahaṃkāra": "Highlight every reference to the nature of the mind — manas, buddhi, ahaṃkāra, and citta.",
    "🙏 Surrender and bhakti": "Flag all teachings specifically about surrender, devotion, and bhakti.",
    "🪞 Ego and its transcendence": "Identify every place where the ego (ahaṃkāra) is discussed.",
    "🧘 Meditation and contemplation": "Mark all practical guidance on meditation, dhyāna, or nididhyāsana.",
    "🌊 Nature of Ātman / Brahman": "Highlight every statement about the nature of Ātman, Brahman, or their identity.",
    "🔗 Cause and effect / Karma": "Flag all references to karma, cause and effect, and their resolution.",
    "✨ Liberation and mokṣa": "Identify every teaching specifically about liberation, mokṣa, or mukti.",
    # Social sharing
    "📱 Top 5 quotable statements": "Identify the 5 most powerful, self-contained, quotable statements from this discourse.",
    "📱 Statements for general audience": "Flag statements that would resonate strongly with a general spiritual audience unfamiliar with Vedānta.",
    "📱 Opening and closing gems": "Highlight the most impactful statement from the opening and closing of the discourse.",
}

col_preset, col_add = st.columns([3, 1])
with col_preset:
    selected_preset = st.selectbox(
        "📋 Choose a focus preset",
        options=list(FOCUS_PRESETS.keys()),
        key="dt_preset_select",
        help="Select a preset to add it to your custom prompt below"
    )
with col_add:
    st.markdown("<br/>", unsafe_allow_html=True)
    add_pressed = st.button("➕ Add", key="dt_add_preset", use_container_width=True)

# Manage the accumulated prompt in session state
if "dt_accumulated_prompt" not in st.session_state:
    st.session_state["dt_accumulated_prompt"] = ""

if add_pressed and FOCUS_PRESETS.get(selected_preset):
    preset_text = FOCUS_PRESETS[selected_preset]
    current = st.session_state["dt_accumulated_prompt"].strip()
    if preset_text not in current:
        st.session_state["dt_accumulated_prompt"] = (
            (current + "\n" + preset_text) if current else preset_text
        )

# Show selected presets as pills
accumulated = st.session_state.get("dt_accumulated_prompt", "")
if accumulated:
    pills = [p.strip() for p in accumulated.split("\n") if p.strip()]
    pills_html = " ".join(
        f"<span style='background:#161616;border:1px solid #c9a96e;border-radius:20px;"
        f"padding:3px 10px;font-size:0.75rem;color:#c9a96e;margin:2px;display:inline-block;'>"
        f"✓ {p[:60]}{'…' if len(p)>60 else ''}</span>"
        for p in pills
    )
    st.markdown(
        f"<div style='margin:0.4rem 0 0.2rem;'>{pills_html}</div>",
        unsafe_allow_html=True
    )
    if st.button("🗑️ Clear all presets", key="dt_clear_presets"):
        st.session_state["dt_accumulated_prompt"] = ""
        st.rerun()

st.markdown(
    "<div style='font-size:0.78rem;color:#555;margin:0.4rem 0 0.3rem;'>"
    "Add your own instructions below, or leave blank to use presets only.</div>",
    unsafe_allow_html=True
)
custom_prompt_extra = st.text_area(
    "Additional custom instructions",
    key="dt_custom_prompt",
    height=90,
    placeholder=(
        "Add your own specific instructions here...\n"
        "e.g. Pay special attention to how Swamiji connects this chapter to daily life."
    ),
    label_visibility="collapsed"
)

# Combine presets + custom into final prompt
_preset_part = st.session_state.get("dt_accumulated_prompt", "").strip()
_custom_part  = custom_prompt_extra.strip()
custom_prompt = "\n".join(filter(None, [_preset_part, _custom_part]))

# ── Step 2 ────────────────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<div class='step-label'>Step 2 — Upload Audio</div>", unsafe_allow_html=True)

audio_files = []
if not openai_key:
    st.warning("⚠️ OpenAI key required. Please add it on the Home page.")
else:
    audio_files = st.file_uploader(
        "Upload audio (MP3, M4A, WAV, OGG)",
        type=["mp3", "m4a", "wav", "ogg"],
        accept_multiple_files=True,
        key="dt_audio"
    )
    if audio_files:
        st.markdown(
            " ".join(f"<span class='file-pill'>🎵 {f.name}</span>" for f in audio_files),
            unsafe_allow_html=True
        )

# ── Step 3 ────────────────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<div class='step-label'>Step 3 — Output Mode</div>", unsafe_allow_html=True)
mode = st.radio(
    "Generate:",
    ["📜 Full structured transcript", "📋 Summary only"],
    horizontal=True, key="dt_mode"
)

# ── Process ───────────────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
if st.button("📜 Transcribe & Structure", key="dt_process", use_container_width=True):
    if not openai_key:
        st.error("OpenAI key required.")
    elif not anthropic_key:
        st.error("Anthropic key required.")
    elif not audio_files:
        st.error("Please upload at least one audio file.")
    else:
        progress = st.progress(0)
        status   = st.empty()
        try:
            # Transcribe
            status.markdown("🎙️ Transcribing audio…")
            chunks = prepare_audio_chunks(audio_files)
            raw = transcribe_chunks(
                chunks, openai_key, progress, status,
                speaker=speaker, scripture=scripture
            )
            st.session_state["dt_raw"] = raw
            progress.progress(50)

            # Structure using helpers.structure_transcript (full transcript)
            status.markdown("✨ Structuring transcript…")
            if mode == "📋 Summary only":
                structured = summarize_text(raw, "Detailed paragraphs", [], anthropic_key)
            else:
                structured = structure_transcript(
                    raw, anthropic_key,
                    speaker=speaker, topic=topic,
                    scripture=scripture, chapter=chapter,
                    verse_range=verse_range,
                    custom_prompt=custom_prompt
                )
            progress.progress(80)

            # Translate if needed
            if output_lang != "English (default)":
                status.markdown(f"🌐 Translating to {output_lang}…")
                structured = translate_text(structured, output_lang, anthropic_key)

            st.session_state["dt_structured"] = structured
            st.session_state["dt_meta"] = {
                "speaker": speaker, "topic": topic,
                "scripture": scripture, "chapter": chapter,
                "verse_range": verse_range, "language": output_lang,
            }
            progress.progress(100)
            status.success("✅ Done!")

        except Exception as e:
            st.error(f"Error: {e}")

# ── Results ───────────────────────────────────────────────────────────────────
if "dt_structured" in st.session_state:
    structured = st.session_state["dt_structured"]
    meta       = st.session_state.get("dt_meta", {})

    st.markdown("<hr style='border-color:#1e1e1e;margin:1.5rem 0;'/>", unsafe_allow_html=True)

    # Discourse header
    st.markdown("""
    <div style='background:#111;border:1px solid #2a2a2a;border-top:4px solid #c9a96e;
    border-radius:12px;padding:1.2rem 1.8rem;margin-bottom:1.5rem;'>
    <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
    letter-spacing:1px;font-weight:600;margin-bottom:0.8rem;'>✦ Discourse Details</div>
    """, unsafe_allow_html=True)

    hc1, hc2, hc3, hc4 = st.columns(4)
    for col, icon, label, val, color in [
        (hc1, "🎙️", "Speaker",   meta.get("speaker","—"), "#e8e0d4"),
        (hc2, "📖", "Topic",     meta.get("topic","—") or "—", "#e8e0d4"),
        (hc3, "📚", "Scripture", meta.get("scripture","—"), "#c9a96e"),
        (hc4, "🌐", "Language",  meta.get("language","—"), "#e8e0d4"),
    ]:
        with col:
            st.markdown(f"**{icon} {label}**")
            st.markdown(
                f"<span style='font-size:0.82rem;font-weight:700;color:{color};'>{val}</span>",
                unsafe_allow_html=True
            )
    if meta.get("chapter") or meta.get("verse_range"):
        st.markdown(
            f"<div style='margin-top:0.6rem;font-size:0.8rem;color:#666;'>"
            f"{'📑 ' + meta['chapter'] if meta.get('chapter') else ''}"
            f"{'  ·  ' if meta.get('chapter') and meta.get('verse_range') else ''}"
            f"{'📿 ' + meta['verse_range'] if meta.get('verse_range') else ''}"
            f"</div>", unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Tabs
    tab_s, tab_r, tab_search = st.tabs(["📜 Structured", "🔤 Raw", "🔍 Search"])

    with tab_s:
        devanagari = re.compile(r'[\u0900-\u097F]{3,}')
        rendered = []
        for line in structured.split("\n"):
            if devanagari.search(line) and not line.strip().startswith("#"):
                rendered.append(
                    f"<div style='text-align:center;font-size:1.1rem;color:#c9a96e;"
                    f"background:#0d0d0d;border-left:3px solid #c9a96e;border-radius:6px;"
                    f"padding:0.6rem 1rem;margin:0.5rem 0;line-height:2;'>{line}</div>"
                )
            else:
                rendered.append(line)
        st.markdown("\n".join(rendered), unsafe_allow_html=True)

    with tab_r:
        raw = st.session_state.get("dt_raw", "")
        if raw:
            st.text_area("Raw transcript", raw, height=400, disabled=True)
        else:
            st.info("Raw transcript not available.")

    with tab_search:
        term = st.text_input("🔍 Search", key="dt_search", placeholder="e.g. Ātman, surrender…")
        if term:
            matches = [
                (i+1, l) for i, l in enumerate(structured.split("\n"))
                if term.lower() in l.lower() and l.strip()
            ]
            st.markdown(
                f"<div style='font-size:0.8rem;color:#888;'>"
                f"{len(matches)} matches for '<b>{term}</b>'</div>",
                unsafe_allow_html=True
            )
            for _, line in matches[:30]:
                hl = re.sub(
                    f"({re.escape(term)})",
                    r"<mark style='background:#c9a96e22;color:#c9a96e;'>\1</mark>",
                    line, flags=re.IGNORECASE
                )
                st.markdown(
                    f"<div style='background:#111;border-left:3px solid #2a2a2a;"
                    f"border-radius:6px;padding:0.5rem 0.8rem;margin-bottom:0.4rem;"
                    f"font-size:0.88rem;color:#b8a88a;'>{hl}</div>",
                    unsafe_allow_html=True
                )

    # Export
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div class='step-label'>Export</div>", unsafe_allow_html=True)
    title_str = " · ".join(filter(None, [
        meta.get("speaker",""), meta.get("topic",""), meta.get("scripture","")
    ])) or "Discourse Transcript"
    header_block = "\n".join([
        f"SPEAKER:   {meta.get('speaker','')}",
        f"TOPIC:     {meta.get('topic','')}",
        f"SCRIPTURE: {meta.get('scripture','')}",
        f"CHAPTER:   {meta.get('chapter','')}",
        f"VERSES:    {meta.get('verse_range','')}",
        f"LANGUAGE:  {meta.get('language','')}",
        "", "─"*50, ""
    ])
    export_content = header_block + structured

    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        st.download_button("📄 TXT", export_content,
                           file_name="discourse_transcript.txt", mime="text/plain")
    with dc2:
        try:
            pdf = make_pdf(title_str, export_content,
                           speaker=meta.get("speaker",""),
                           topic=meta.get("topic",""),
                           scripture=meta.get("scripture",""),
                           language=meta.get("language",""))
            st.download_button("📕 PDF", pdf,
                               file_name="discourse_transcript.pdf",
                               mime="application/pdf")
        except Exception as e:
            st.caption(f"PDF: {e}")
    with dc3:
        try:
            docx = make_docx(title_str, export_content)
            st.download_button("📘 DOCX", docx,
                               file_name="discourse_transcript.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        except Exception as e:
            st.caption(f"DOCX: {e}")


    # ── My Reflections ────────────────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#0d0d0d;border:1px solid #2a2a2a;border-left:3px solid #c9a96e;
    border-radius:10px;padding:1rem 1.4rem;margin-bottom:0.5rem;'>
        <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
        letter-spacing:1px;margin-bottom:0.3rem;'>🪷 My Reflections — Manana & Nididhyāsana</div>
        <div style='font-size:0.8rem;color:#555;'>
        Add your own notes, questions, or insights below.
        These will be included when you download the PDF or DOCX.
        </div>
    </div>
    """, unsafe_allow_html=True)
    reflection = st.text_area(
        "My reflections",
        key="reflection_transcriber",
        height=150,
        placeholder=(
            "What struck me most in this discourse...\n"
            "Questions that arose for me...\n"
            "How I can apply this teaching...\n"
            "Sanskrit terms I want to explore further..."
        ),
        label_visibility="collapsed"
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🔄 Clear and start over", key="dt_clear"):
        for k in ["dt_structured", "dt_raw", "dt_meta"]:
            st.session_state.pop(k, None)
        st.rerun()
