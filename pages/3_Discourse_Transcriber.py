import streamlit as st
import sys
import os
import json
import re
import tempfile
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
    prepare_audio_chunks, split_audio_ffmpeg,
    transcribe_chunks, translate_text,
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
    Upload a discourse audio file. The AI will produce a
    <b style='color:#b8a88a;'>polished, structured transcript</b> with auto-generated
    section headings, Sanskrit verses in <b style='color:#c9a96e;'>Devanāgarī script</b>,
    bullet points, and a summary — ready to study, archive, or export.
</div>
""", unsafe_allow_html=True)

SPEAKERS = [
    "Swāmī Aparājitānandajī",
    "Swāmī Śaraṇānandajī",
    "Other / Not specified",
]

SCRIPTURES = [
    "Bhagavad Gītā", "Upaniṣads", "Vivekachūḍāmaṇi", "Tattva Bodha",
    "Bhaja Govindam", "Soundarya Laharī", "Kaṭhopaniṣad",
    "Māṇḍūkya Upaniṣad", "Īśāvāsya Upaniṣad", "Muṇḍaka Upaniṣad",
    "Yoga Vāsiṣṭha", "Srimad Bhāgavatam", "Rāmāyaṇa / Sundara Kāṇḍa",
    "Other / Not specified",
]

def build_prompt(speaker, topic, scripture, chapter, verse_range, language, mode):
    lang_note = (f"The entire output MUST be in {language}. " if language != "English (default)" else "")
    summary_only = (mode == "📋 Summary only")
    structure_note = (
        "Generate ONLY: Concise Summary, Key Takeaways, Sanskrit Terms Glossary, "
        "Practical Reflection, and Main Philosophical Insights."
        if summary_only else
        "Organize into clearly headed sections (## Introduction, ## Main Teaching, etc.). "
        "Include EVERY sentence — do NOT summarize or skip anything. "
        "This is a full structured transcript, not a summary."
    )
    return f"""You are an expert Vedantic discourse transcriber.
{lang_note}
Speaker: {speaker or 'Not specified'} | Topic: {topic or 'Not specified'}
Scripture: {scripture or 'Not specified'} | Chapter: {chapter or 'Not specified'} | Verses: {verse_range or 'Not specified'}

CLEANUP: Fix grammar, remove filler words, preserve meaning and devotional tone.
SANSKRIT: ALL Sanskrit verses MUST appear in Devanāgarī script only (e.g. ॐ तत् सत्). Never transliterate verses to Roman script.
STRUCTURE: {structure_note}
END SECTIONS (always add): ## Concise Summary | ## Key Takeaways | ## Sanskrit Terms Glossary | ## Practical Reflection
"""

st.markdown("<div class='step-label'>Step 1 — Discourse Details</div>", unsafe_allow_html=True)

d1, d2 = st.columns(2)
with d1:
    speaker = st.selectbox("🎙️ Speaker", SPEAKERS, key="dt_speaker")
    if speaker == "Other / Not specified":
        speaker = st.text_input("Enter speaker name", key="dt_speaker_other", placeholder="e.g. Swāmī Tejomayānandajī")
with d2:
    topic = st.text_input("📖 Topic / Title", key="dt_topic", placeholder="e.g. Introduction to Vivekachūḍāmaṇi")

d3, d4, d5 = st.columns(3)
with d3:
    scripture = st.selectbox("📚 Scripture", SCRIPTURES, key="dt_scripture")
    if scripture == "Other / Not specified":
        scripture = st.text_input("Enter scripture", key="dt_scripture_other")
with d4:
    chapter = st.text_input("📑 Chapter", key="dt_chapter", placeholder="e.g. Chapter 2")
with d5:
    verse_range = st.text_input("📿 Verse Range", key="dt_verse", placeholder="e.g. Verses 3–7")

lang_options = list(LANGUAGES.keys())
output_lang = st.selectbox("🌐 Output Language", lang_options, key="dt_lang")

st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<div class='step-label'>Step 2 — Upload Audio</div>", unsafe_allow_html=True)

if not openai_key:
    st.warning("⚠️ OpenAI key required for transcription. Please add it on the Home page.")
else:
    audio_files = st.file_uploader(
        "Upload audio (MP3, M4A, WAV, OGG — up to 5 files)",
        type=["mp3", "m4a", "wav", "ogg"],
        accept_multiple_files=True,
        key="dt_audio"
    )
    if audio_files:
        st.markdown(
            " ".join(f"<span class='file-pill'>🎵 {f.name}</span>" for f in audio_files),
            unsafe_allow_html=True
        )

st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<div class='step-label'>Step 3 — Output Mode</div>", unsafe_allow_html=True)
mode = st.radio("Generate:", ["📜 Full structured transcript", "📋 Summary only"], horizontal=True, key="dt_mode")

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
            # Step A — Transcribe
            status.markdown("🎙️ Transcribing audio…")
            chunks = prepare_audio_chunks(audio_files)
            raw_transcript = transcribe_chunks(
                chunks, openai_key, progress, status,
                speaker=speaker, scripture=scripture
            )
            st.session_state["dt_raw"] = raw_transcript
            progress.progress(50)

            # Step B — Structure using anthropic SDK (same as Audio Summarizer)
            status.markdown("✨ Structuring transcript…")
            import anthropic as _ant
            client = _ant.Anthropic(api_key=anthropic_key)

            prompt = build_prompt(speaker, topic, scripture, chapter, verse_range, output_lang, mode)

            # Split into chunks if very long
            CHUNK = 80000
            text  = raw_transcript
            parts = []
            pos, chunk_num = 0, 0
            total_chunks = max(1, (len(text) + CHUNK - 1) // CHUNK)

            while pos < len(text):
                chunk_num += 1
                end = min(pos + CHUNK, len(text))
                if end < len(text):
                    b = text.rfind(". ", pos, end)
                    if b != -1: end = b + 1
                chunk = text[pos:end]
                pos = end

                if total_chunks > 1:
                    status.markdown(f"✨ Structuring part {chunk_num}/{total_chunks}…")
                    progress.progress(50 + int(40 * chunk_num / total_chunks))

                note = ""
                if total_chunks > 1:
                    note = (
                        f"\n\nPart {chunk_num}/{total_chunks}. Structure fully. No end sections yet."
                        if chunk_num < total_chunks else
                        f"\n\nFinal part {chunk_num}/{total_chunks}. Structure and add all end sections."
                    )

                msg = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=8000,
                    system=prompt + note,
                    messages=[{"role": "user", "content": chunk}]
                )
                part = msg.content[0].text.strip()
                parts.append(("\n\n---\n\n" + part) if chunk_num > 1 else part)

            structured = "\n".join(parts)

            if output_lang != "English (default)":
                status.markdown(f"🌐 Translating to {output_lang}…")
                structured = translate_text(structured, output_lang, anthropic_key)

            st.session_state["dt_structured"] = structured
            st.session_state["dt_meta"] = {
                "speaker": speaker, "topic": topic, "scripture": scripture,
                "chapter": chapter, "verse_range": verse_range,
                "language": output_lang, "mode": mode
            }
            progress.progress(100)
            status.success("✅ Done!")

        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Tip: If the audio is very long, try splitting into shorter segments.")

# ── Results ───────────────────────────────────────────────────────────────────
if "dt_structured" in st.session_state:
    structured = st.session_state["dt_structured"]
    meta       = st.session_state.get("dt_meta", {})

    st.markdown("<hr style='border-color:#1e1e1e;margin:1.5rem 0;'/>", unsafe_allow_html=True)

    # Header
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
            st.markdown(f"<span style='font-size:0.82rem;font-weight:700;color:{color};'>{val}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Tabs
    tab_s, tab_r, tab_search = st.tabs(["📜 Structured", "🔤 Raw", "🔍 Search"])

    with tab_s:
        # Highlight Devanagari lines
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
            matches = [(i+1, l) for i, l in enumerate(structured.split("\n")) if term.lower() in l.lower() and l.strip()]
            st.markdown(f"<div style='font-size:0.8rem;color:#888;'>{len(matches)} matches for '<b>{term}</b>'</div>", unsafe_allow_html=True)
            for _, line in matches[:30]:
                hl = re.sub(f"({re.escape(term)})", r"<mark style='background:#c9a96e22;color:#c9a96e;'>\1</mark>", line, flags=re.IGNORECASE)
                st.markdown(f"<div style='background:#111;border-left:3px solid #2a2a2a;border-radius:6px;padding:0.5rem 0.8rem;margin-bottom:0.4rem;font-size:0.88rem;color:#b8a88a;'>{hl}</div>", unsafe_allow_html=True)

    # Export
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div class='step-label'>Export</div>", unsafe_allow_html=True)
    title_str = " · ".join(filter(None, [meta.get("speaker",""), meta.get("topic",""), meta.get("scripture","")])) or "Discourse Transcript"
    header_block = "\n".join([
        f"SPEAKER: {meta.get('speaker','')}",
        f"TOPIC: {meta.get('topic','')}",
        f"SCRIPTURE: {meta.get('scripture','')}",
        f"CHAPTER: {meta.get('chapter','')}",
        f"VERSES: {meta.get('verse_range','')}",
        f"LANGUAGE: {meta.get('language','')}",
        "", "─"*50, ""
    ])
    export_content = header_block + structured

    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        st.download_button("📄 TXT", export_content, file_name="discourse_transcript.txt", mime="text/plain")
    with dc2:
        try:
            pdf = make_pdf(title_str, export_content, speaker=meta.get("speaker",""), topic=meta.get("topic",""), scripture=meta.get("scripture",""), language=meta.get("language",""))
            st.download_button("📕 PDF", pdf, file_name="discourse_transcript.pdf", mime="application/pdf")
        except Exception as e:
            st.caption(f"PDF: {e}")
    with dc3:
        try:
            docx = make_docx(title_str, export_content)
            st.download_button("📘 DOCX", docx, file_name="discourse_transcript.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        except Exception as e:
            st.caption(f"DOCX: {e}")

    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🔄 Clear and start over", key="dt_clear"):
        for k in ["dt_structured", "dt_raw", "dt_meta"]:
            st.session_state.pop(k, None)
        st.rerun()
