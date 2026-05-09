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
        if st.button("🏠 Home", key="home_btn_" + __file__[-20:]):
            st.switch_page("app.py")
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>", unsafe_allow_html=True)

# ── Keys ──────────────────────────────────────────────────────────────────────
anthropic_key = st.session_state.get("anthropic_key", "")
openai_key    = st.session_state.get("openai_key", "")
if not anthropic_key:
    try: anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
    except: pass
if not openai_key:
    try: openai_key = st.secrets["OPENAI_API_KEY"]
    except: pass

# ── Hero ──────────────────────────────────────────────────────────────────────
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

# ══════════════════════════════════════════════════════════════════════════════
# DISCOURSE CLEANUP + STRUCTURING PROMPT
# ══════════════════════════════════════════════════════════════════════════════
def build_structuring_prompt(speaker, topic, scripture, chapter, verse_range, language):
    lang_note = (
        f"The entire structured output MUST be in {language}. "
        if language != "English (default)" else ""
    )
    return f"""You are an expert Vedantic discourse transcriber and spiritual content formatter.

You will receive a raw audio transcript of a spiritual discourse. Your task is to transform it
into a beautifully structured, polished, and readable document — like a high-quality Vedantic
study notebook.

DISCOURSE METADATA:
- Speaker: {speaker or 'Not specified'}
- Topic: {topic or 'Not specified'}
- Scripture: {scripture or 'Not specified'}
- Chapter/Section: {chapter or 'Not specified'}
- Verse Range: {verse_range or 'Not specified'}

{lang_note}

==============================================================
TRANSCRIPT CLEANUP RULES
==============================================================
1. Remove conversational repetitions ("you know… you know…", repeated partial phrases, filler words like "so", "now", "okay", "right").
2. Fix grammar and sentence flow WITHOUT changing meaning or philosophical depth.
3. Make minor corrections to improve readability while preserving the speaker's tone, devotion, and authenticity.
4. Do NOT over-edit. Maintain the natural discourse style.
5. Preserve the speaker's rhetorical questions — they are intentional teaching devices.

==============================================================
SANSKRIT & SCRIPTURE RULES — CRITICAL
==============================================================
1. Detect ALL Sanskrit verses, shlokas, and mantras automatically.
2. Render EVERY Sanskrit verse in proper Devanāgarī script ONLY.
   Example: श्रेयान्स्वधर्मो विगुणः परधर्मात्स्वनुष्ठितात्
3. Do NOT transliterate Sanskrit verses into Roman/English script.
4. Format each verse as a distinct visual block — centered, on its own line.
5. After the Devanāgarī verse, provide its meaning in the output language.
6. Include verse references precisely:
   Example: Bhagavad Gītā 2.47 | Kaṭhopaniṣad 1.2.20
7. Never fabricate or hallucinate scripture references.

==============================================================
DOCUMENT STRUCTURE
==============================================================
Organize the transcript into clearly headed sections. Use meaningful headings such as:
## Introduction
## Opening Prayer / Invocation
## Context and Background
## Main Teaching
## Key Vedantic Insight
## Scriptural Explanation
## Story / Analogy
## Practical Application
## Reflection for Seekers
## Summary and Takeaways

Rules:
- Generate only the sections that are actually present in the discourse.
- Do not invent sections for content that was not spoken.
- Use ### for subsections within a section.

==============================================================
LISTS & TABLES
==============================================================
- If the speaker mentions multiple steps, qualities, examples, or categories — convert to bullet points or numbered lists.
- If a concept is better shown comparatively (e.g. Jeevātma vs Paramātma, Karma vs Bhakti vs Jñāna) — create a clean markdown table.
- Tables must have clear headers and aligned columns.

==============================================================
END SECTION — always include these at the end
==============================================================

## 📋 Concise Summary
One paragraph capturing the essence of the discourse.

## 🔑 Key Takeaways
Bullet list of the most important teachings.

## 🕉️ Sanskrit Terms Glossary
| Term | Devanāgarī | Meaning |
|------|-----------|---------|
List all significant Sanskrit terms used with their Devanāgarī and meaning.

## 💡 Practical Reflection
1–2 sentences for the seeker: what to contemplate or practise from this discourse.

## 🌟 Main Philosophical Insights
Bullet list of the core philosophical points made in this discourse.

==============================================================
TONE & STYLE
==============================================================
- Reverential, clear, and devotional in tone.
- Readable for sincere seekers of all backgrounds.
- Preserve philosophical precision — never simplify at the cost of accuracy.
- Format must render beautifully in both web UI and exported documents.

==============================================================
CRITICAL — OUTPUT COMPLETENESS
==============================================================
- You MUST include the COMPLETE structured transcript of EVERY sentence spoken.
- Do NOT summarize, condense, or skip any portion of the transcript.
- Do NOT stop early — process every word given to you.
- This is a full transcript tool, NOT a summarizer.
- Every teaching, example, analogy, and explanation must appear in the output.

Now transform the following raw transcript:
"""


def _claude_call(system: str, user: str, anthropic_key: str, max_tokens: int = 4000) -> str:
    """Single Claude API call."""
    import urllib.request
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": anthropic_key,
            "anthropic-version": "2023-06-01"
        }
    )
    with urllib.request.urlopen(req, timeout=55) as resp:
        data = json.loads(resp.read())
    return data["content"][0]["text"].strip()


def call_structuring_api(raw_transcript: str, prompt: str, anthropic_key: str) -> str:
    """Structure transcript. Splits into chunks if very long (>12000 chars)."""
    CHUNK_SIZE = 8000    # characters per chunk (~2000 words) — keeps each call under 60s
    OVERLAP    = 300     # overlap to avoid losing context at boundaries

    if len(raw_transcript) <= CHUNK_SIZE:
        # Short enough — process in one call
        return _claude_call(prompt, raw_transcript, anthropic_key, max_tokens=4000)

    # Long discourse — chunk it, structure each part, then merge
    chunks = []
    start  = 0
    while start < len(raw_transcript):
        end = min(start + CHUNK_SIZE, len(raw_transcript))
        # Try to break at a sentence boundary
        if end < len(raw_transcript):
            boundary = raw_transcript.rfind(". ", start + CHUNK_SIZE - 200, end)
            if boundary != -1:
                end = boundary + 1
        chunks.append(raw_transcript[start:end])
        start = end - OVERLAP

    total = len(chunks)
    structured_parts = []

    for i, chunk in enumerate(chunks, 1):
        part_prompt = prompt + (
            f"\n\nNOTE: This is PART {i} of {total} of the discourse transcript. "
            f"Structure only this portion. Do NOT add the end summary sections "
            f"(Summary, Key Takeaways, Glossary, Reflection, Insights) — "
            f"those will be added after the final part."
            if i < total else
            f"\n\nNOTE: This is the FINAL PART ({i} of {total}). "
            f"Structure this portion AND include the full end sections "
            f"(Concise Summary, Key Takeaways, Sanskrit Terms Glossary, "
            f"Practical Reflection, Main Philosophical Insights) "
            f"based on the ENTIRE discourse, not just this final chunk."
        )
        part_result = _claude_call(part_prompt, chunk, anthropic_key, max_tokens=4000)
        structured_parts.append(f"\n\n---\n\n" + part_result if i > 1 else part_result)

    return "\n".join(structured_parts)


def render_structured_transcript(text: str):
    """Render the structured transcript with beautiful formatting."""
    # Convert markdown tables to HTML for better rendering
    lines = text.split("\n")
    in_table = False
    html_parts = []
    md_parts   = []

    for line in lines:
        if line.strip().startswith("|") and "|" in line[1:]:
            in_table = True
            md_parts.append(line)
        else:
            if in_table:
                # Flush table
                html_parts.append(("table", "\n".join(md_parts)))
                md_parts = []
                in_table = False
            html_parts.append(("text", line))

    if md_parts:
        html_parts.append(("table", "\n".join(md_parts)))

    # Render each block
    text_block = []
    for kind, content in html_parts:
        if kind == "table":
            st.markdown(content)
        else:
            text_block.append(content)

    # Render all non-table content
    full_text = "\n".join(
        c for k, c in html_parts if k == "text"
    )

    # Highlight Sanskrit blocks (lines that are primarily Devanagari)
    devanagari_pattern = re.compile(r'[\u0900-\u097F]{3,}')
    rendered_lines = []
    for line in full_text.split("\n"):
        if devanagari_pattern.search(line) and not line.strip().startswith("#"):
            rendered_lines.append(
                f"<div style='text-align:center;font-size:1.15rem;color:#c9a96e;"
                f"background:#0d0d0d;border-left:3px solid #c9a96e;border-radius:6px;"
                f"padding:0.6rem 1rem;margin:0.5rem 0;line-height:2;'>{line}</div>"
            )
        else:
            rendered_lines.append(line)

    st.markdown("\n".join(rendered_lines), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — DISCOURSE DETAILS HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='step-label'>Step 1 — Discourse Details</div>", unsafe_allow_html=True)
st.markdown(
    "<div style='font-size:0.82rem;color:#666;margin-bottom:0.8rem;'>"
    "These details help the AI structure and label the transcript accurately.</div>",
    unsafe_allow_html=True
)

SPEAKERS = [
    "Swāmī Aparājitānandajī",
    "Swāmī Śaraṇānandajī",
    "Other / Not specified",
]

SCRIPTURES = [
    "Bhagavad Gītā",
    "Upaniṣads",
    "Vivekachūḍāmaṇi",
    "Tattva Bodha",
    "Bhaja Govindam",
    "Soundarya Laharī",
    "Kaṭhopaniṣad",
    "Māṇḍūkya Upaniṣad",
    "Īśāvāsya Upaniṣad",
    "Aitareya Upaniṣad",
    "Muṇḍaka Upaniṣad",
    "Yoga Vāsiṣṭha",
    "Srimad Bhāgavatam",
    "Rāmāyaṇa / Sundara Kāṇḍa",
    "Other / Not specified",
]

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
    scripture = st.selectbox("📚 Scripture / Text", SCRIPTURES, key="dt_scripture")
    if scripture == "Other / Not specified":
        scripture = st.text_input("Enter scripture", key="dt_scripture_other",
                                  placeholder="e.g. Aparokṣānubhūti")
with d4:
    chapter = st.text_input("📑 Chapter / Section", key="dt_chapter",
                            placeholder="e.g. Chapter 2, Day 3")
with d5:
    verse_range = st.text_input("📿 Verse Range", key="dt_verse",
                                placeholder="e.g. Verses 3–7, Mantra 5")

lang_options = list(LANGUAGES.keys())
output_lang = st.selectbox("🌐 Output Language", lang_options, key="dt_lang")

# ── Upload ────────────────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<div class='step-label'>Step 2 — Upload Audio</div>", unsafe_allow_html=True)

if not openai_key:
    st.warning("⚠️ OpenAI key required for transcription. Please add it on the Home page.")
else:
    audio_files = st.file_uploader(
        "Upload audio file(s) — MP3, M4A, WAV, OGG (up to 5)",
        type=["mp3", "m4a", "wav", "ogg"],
        accept_multiple_files=True,
        key="dt_audio"
    )

    if audio_files:
        st.markdown(
            " ".join(
                f"<span class='file-pill'>🎵 {f.name} · {f.size//1024//1024 or '<1'}MB</span>"
                for f in audio_files
            ),
            unsafe_allow_html=True
        )

# ── Mode ──────────────────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<div class='step-label'>Step 3 — Output Mode</div>", unsafe_allow_html=True)

mode = st.radio(
    "What would you like to generate?",
    ["📜 Full structured transcript", "📋 Summary only"],
    horizontal=True,
    key="dt_mode"
)

# ── Process ───────────────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
if st.button("📜 Transcribe & Structure", key="dt_process", use_container_width=True):
    if not openai_key:
        st.error("OpenAI key required for transcription.")
    elif not anthropic_key:
        st.error("Anthropic key required for structuring.")
    elif not audio_files:
        st.error("Please upload at least one audio file.")
    else:
        progress = st.progress(0)
        status   = st.empty()

        # Step A — Transcribe
        status.markdown("🎙️ Transcribing audio…")
        try:
            chunks = prepare_audio_chunks(audio_files)
            raw_transcript = transcribe_chunks(
                chunks, openai_key, progress, status,
                speaker=speaker, scripture=scripture
            )
            st.session_state["dt_raw"] = raw_transcript
            progress.progress(50)
        except Exception as e:
            st.error(f"Transcription failed: {e}")
            st.stop()

        # Step B — Structure with Claude (chunk by chunk with progress updates)
        status.markdown("✨ Structuring transcript…")
        try:
            prompt = build_structuring_prompt(
                speaker, topic, scripture, chapter, verse_range, output_lang
            )
            if mode == "📋 Summary only":
                prompt += (
                    "\n\nIMPORTANT: Generate ONLY: Concise Summary, Key Takeaways, "
                    "Sanskrit Terms Glossary, Practical Reflection, and Main Philosophical Insights."
                )

            CHUNK = 4000
            text = raw_transcript
            parts = []
            total_chunks = max(1, (len(text) + CHUNK - 1) // CHUNK)

            pos = 0
            chunk_num = 0
            while pos < len(text):
                chunk_num += 1
                end = min(pos + CHUNK, len(text))
                # break at sentence boundary
                if end < len(text):
                    b = text.rfind(". ", pos, end)
                    if b != -1:
                        end = b + 1
                chunk = text[pos:end]
                pos = end

                if total_chunks > 1:
                    status.markdown(f"✨ Structuring part {chunk_num} of {total_chunks}…")
                    progress.progress(50 + int(40 * chunk_num / total_chunks))

                note = ""
                if total_chunks > 1:
                    if chunk_num < total_chunks:
                        note = (f"\n\nNOTE: Part {chunk_num}/{total_chunks}. "
                                f"Structure this portion only. No summary sections yet.")
                    else:
                        note = (f"\n\nNOTE: Final part {chunk_num}/{total_chunks}. "
                                f"Structure this AND add full end sections.")

                import urllib.request as _ur
                payload = json.dumps({
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 6000,
                    "system": prompt + note,
                    "messages": [{"role": "user", "content": chunk}]
                }).encode()
                req = _ur.Request(
                    "https://api.anthropic.com/v1/messages",
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": anthropic_key,
                        "anthropic-version": "2023-06-01"
                    }
                )
                with _ur.urlopen(req, timeout=55) as resp:
                    data = json.loads(resp.read())
                part = data["content"][0]["text"].strip()
                parts.append(("\n\n---\n\n" + part) if chunk_num > 1 else part)

            structured = "\n".join(parts)

            # Translate if needed
            if output_lang != "English (default)":
                status.markdown(f"🌐 Translating to {output_lang}…")
                structured = translate_text(structured, output_lang, anthropic_key)

            st.session_state["dt_structured"] = structured
            st.session_state["dt_meta"] = {
                "speaker": speaker, "topic": topic,
                "scripture": scripture, "chapter": chapter,
                "verse_range": verse_range, "language": output_lang,
                "mode": mode
            }
            progress.progress(100)
            status.success("✅ Done!")
        except Exception as e:
            st.error(f"Structuring failed: {e}")
            st.error("Tip: If the audio is very long, try splitting it into shorter segments.")

# ══════════════════════════════════════════════════════════════════════════════
# RESULTS
# ══════════════════════════════════════════════════════════════════════════════
if "dt_structured" in st.session_state:
    structured = st.session_state["dt_structured"]
    meta       = st.session_state.get("dt_meta", {})

    st.markdown("<hr style='border-color:#1e1e1e;margin:1.5rem 0;'/>", unsafe_allow_html=True)

    # ── Discourse header display ───────────────────────────────────────────────
    st.markdown("""
    <div style='background:#111;border:1px solid #2a2a2a;border-top:4px solid #c9a96e;
    border-radius:12px;padding:1.2rem 1.8rem;margin-bottom:1.5rem;'>
    <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
    letter-spacing:1px;font-weight:600;margin-bottom:0.8rem;'>✦ Discourse Details</div>
    """, unsafe_allow_html=True)

    hc1, hc2, hc3, hc4 = st.columns(4)
    for col, icon, label, val in [
        (hc1, "🎙️", "Speaker",   meta.get("speaker", "—")),
        (hc2, "📖", "Topic",     meta.get("topic", "—") or "—"),
        (hc3, "📚", "Scripture", meta.get("scripture", "—")),
        (hc4, "🌐", "Language",  meta.get("language", "—")),
    ]:
        with col:
            st.markdown(f"**{icon} {label}**")
            color = "#c9a96e" if label == "Scripture" else "#e8e0d4"
            st.markdown(
                f"<span style='font-size:0.82rem;font-weight:700;color:{color};'>{val}</span>",
                unsafe_allow_html=True
            )

    if meta.get("chapter") or meta.get("verse_range"):
        st.markdown(
            f"<div style='margin-top:0.6rem;font-size:0.8rem;color:#666;'>"
            f"{'📑 ' + meta['chapter'] if meta.get('chapter') else ''}"
            f"{'&nbsp;&nbsp;·&nbsp;&nbsp;' if meta.get('chapter') and meta.get('verse_range') else ''}"
            f"{'📿 ' + meta['verse_range'] if meta.get('verse_range') else ''}"
            f"</div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Tabs: Structured view | Raw transcript ─────────────────────────────────
    tab_structured, tab_raw, tab_search = st.tabs(
        ["📜 Structured Transcript", "🔤 Raw Transcript", "🔍 Search"]
    )

    with tab_structured:
        st.markdown(
            "<div class='output-box' style='max-height:none;overflow:visible;'>",
            unsafe_allow_html=True
        )
        render_structured_transcript(structured)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_raw:
        raw = st.session_state.get("dt_raw", "")
        if raw:
            st.text_area("Raw transcript", raw, height=400, disabled=True, key="dt_raw_view")
        else:
            st.info("Raw transcript not available.")

    with tab_search:
        search_term = st.text_input("🔍 Search within transcript", key="dt_search",
                                    placeholder="e.g. Ātman, surrender, ego…")
        if search_term and structured:
            matches = [
                (i+1, line) for i, line in enumerate(structured.split("\n"))
                if search_term.lower() in line.lower() and line.strip()
            ]
            if matches:
                st.markdown(
                    f"<div style='font-size:0.8rem;color:#888;margin-bottom:0.5rem;'>"
                    f"Found <b style='color:#c9a96e;'>{len(matches)}</b> matches for "
                    f"'<b>{search_term}</b>'</div>",
                    unsafe_allow_html=True
                )
                for line_no, line in matches[:30]:
                    highlighted = re.sub(
                        f"({re.escape(search_term)})",
                        r"<mark style='background:#c9a96e22;color:#c9a96e;"
                        r"border-radius:3px;padding:0 2px;'>\1</mark>",
                        line,
                        flags=re.IGNORECASE
                    )
                    st.markdown(
                        f"<div style='background:#111;border-left:3px solid #2a2a2a;"
                        f"border-radius:6px;padding:0.5rem 0.8rem;margin-bottom:0.4rem;"
                        f"font-size:0.88rem;color:#b8a88a;'>{highlighted}</div>",
                        unsafe_allow_html=True
                    )
                if len(matches) > 30:
                    st.caption(f"Showing first 30 of {len(matches)} matches.")
            else:
                st.info(f"No matches found for '{search_term}'.")

    # ── Copy to clipboard ──────────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("📋 Copy transcript to clipboard", key="dt_copy"):
        st.code(structured, language=None)
        st.caption("Select all text above and copy.")

    # ── Downloads ──────────────────────────────────────────────────────────────
    st.markdown("<div class='step-label'>Export</div>", unsafe_allow_html=True)

    title_str = " · ".join(filter(None, [
        meta.get("speaker",""), meta.get("topic",""), meta.get("scripture","")
    ])) or "Discourse Transcript"

    # Build a rich header block prepended to content for exports
    header_lines = [
        f"# Discourse Transcript",
        f"",
        f"**Speaker:** {meta.get('speaker','')}",
        f"**Topic:** {meta.get('topic','')}",
        f"**Scripture:** {meta.get('scripture','')}",
    ]
    if meta.get("chapter"):
        header_lines.append(f"**Chapter/Section:** {meta.get('chapter','')}")
    if meta.get("verse_range"):
        header_lines.append(f"**Verse Range:** {meta.get('verse_range','')}")
    header_lines.append(f"**Language:** {meta.get('language','')}")
    header_lines += ["", "---", ""]
    export_content = "\n".join(header_lines) + "\n" + structured

    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        st.download_button(
            "📄 Download TXT",
            export_content,
            file_name="discourse_transcript.txt",
            mime="text/plain"
        )
    with dc2:
        try:
            pdf = make_pdf(
                title_str, export_content,
                speaker=meta.get("speaker",""),
                topic=meta.get("topic",""),
                scripture=meta.get("scripture",""),
                language=meta.get("language","")
            )
            st.download_button(
                "📕 Download PDF", pdf,
                file_name="discourse_transcript.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.caption(f"PDF: {e}")
    with dc3:
        try:
            # make_docx takes only title + content
            docx = make_docx(title_str, export_content)
            st.download_button(
                "📘 Download DOCX", docx,
                file_name="discourse_transcript.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        except Exception as e:
            st.caption(f"DOCX: {e}")

    # ── Clear ──────────────────────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🔄 Clear and start over", key="dt_clear"):
        for k in ["dt_structured", "dt_raw", "dt_meta"]:
            st.session_state.pop(k, None)
        st.rerun()


