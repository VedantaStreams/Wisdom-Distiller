import streamlit as st
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.styles import SHARED_CSS
from utils.usage_tracker import check_usage_limit, increment_usage, show_usage_badge
from utils.helpers import (
    prepare_audio_chunks, transcribe_chunks,
    summarize_text, translate_text, analyze_discourse,
    make_pdf, make_docx,
    TABLE_COLUMNS, markdown_table_to_html, TABLE_CSS, LANGUAGES
)

st.set_page_config(
    page_title="Audio Summarizer · Wisdom Distiller",
    page_icon="🎙️", layout="centered"
)
st.markdown(SHARED_CSS, unsafe_allow_html=True)

anthropic_key = st.session_state.get("anthropic_key", "")
openai_key = st.session_state.get("openai_key", "")
if not anthropic_key:
    try: anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
    except: pass
if not openai_key:
    try: openai_key = st.secrets["OPENAI_API_KEY"]
    except: pass

st.markdown("""
<div class="hero">
    <h1>🎙️ Audio <span class="accent">Summarizer</span></h1>
    <p class="subtitle">Upload up to 5 audio segments · Transcribe · Summarize · Export</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="about-box">
    Upload a single long audio file <b>or</b> up to 5 shorter segments recorded in sequence.
    Files are transcribed in the order uploaded and combined into one unified summary.
    Supports <b>MP3, M4A, WAV, OGG</b>.
</div>
""", unsafe_allow_html=True)


# ── Helper: show insights panel ────────────────────────────────────────────────
def show_insights(insights: dict):
    scriptures = insights.get("scriptures", [])
    key_terms = insights.get("key_terms", [])
    scripture_str = " · ".join(scriptures) if scriptures else "None identified"
    terms_str = " · ".join(key_terms) if key_terms else "None identified"
    scripture_text = insights.get("scripture_text", "")

    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:12px;"
        " padding:1.2rem 1.5rem; margin-bottom:1rem;'>"
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem;"
        " color:#c9a96e; font-weight:600; margin-bottom:0.8rem;'>📋 Discourse Insights</div>"
        "<div style='display:grid; grid-template-columns:150px 1fr; gap:0.5rem;"
        " font-size:0.84rem; line-height:1.85;'>"
        "<div style='color:#666;'>🎙️ Speaker</div>"
        f"<div style='color:#e8e0d4;'>{insights.get('speaker', 'Unknown')}</div>"
        "<div style='color:#666;'>📖 Topic</div>"
        f"<div style='color:#e8e0d4;'>{insights.get('topic', 'Unknown')}</div>"
        + (
            "<div style='color:#666;'>📚 Scripture / Text</div>"
            f"<div style='color:#e8e0d4;'>{scripture_text}</div>"
            if scripture_text else ""
        ) +
        "<div style='color:#666;'>🕉️ Tradition</div>"
        f"<div style='color:#e8e0d4;'>{insights.get('tradition', 'Unknown')}</div>"
        "<div style='color:#666;'>📜 Verses Referenced</div>"
        f"<div style='color:#c9a96e;'>{scripture_str}</div>"
        "<div style='color:#666;'>🔑 Key Terms</div>"
        f"<div style='color:#b8a88a; font-style:italic;'>{terms_str}</div>"
        "</div></div>",
        unsafe_allow_html=True
    )


# ── Helper: show all download buttons persistently ────────────────────────────
def show_downloads(title, summary, transcript, output_format):
    st.markdown("#### ⬇️ Downloads")
    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:10px;"
        " padding:1rem 1.4rem; margin-bottom:0.5rem;'>"
        "<div style='font-size:0.8rem; color:#666; margin-bottom:0.6rem;'>Summary</div>",
        unsafe_allow_html=True
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "⬇️ TXT", data=summary,
            file_name="summary.txt", mime="text/plain",
            key="dl_summary_txt"
        )
    with c2:
        pdf_bytes = make_pdf(title, summary)
        st.download_button(
            "⬇️ PDF", data=pdf_bytes,
            file_name="summary.pdf", mime="application/pdf",
            key="dl_summary_pdf"
        )
    with c3:
        docx_bytes = make_docx(title, summary)
        st.download_button(
            "⬇️ DOCX", data=docx_bytes,
            file_name="summary.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="dl_summary_docx"
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:10px;"
        " padding:1rem 1.4rem;'>"
        "<div style='font-size:0.8rem; color:#666; margin-bottom:0.6rem;'>Full Transcript</div>",
        unsafe_allow_html=True
    )
    t1, t2, t3 = st.columns(3)
    with t1:
        st.download_button(
            "⬇️ TXT", data=transcript,
            file_name="transcript.txt", mime="text/plain",
            key="dl_transcript_txt"
        )
    with t2:
        pdf_tr = make_pdf(title + " — Transcript", transcript)
        st.download_button(
            "⬇️ PDF", data=pdf_tr,
            file_name="transcript.pdf", mime="application/pdf",
            key="dl_transcript_pdf"
        )
    with t3:
        docx_tr = make_docx(title + " — Transcript", transcript)
        st.download_button(
            "⬇️ DOCX", data=docx_tr,
            file_name="transcript.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="dl_transcript_docx"
        )
    st.markdown("</div>", unsafe_allow_html=True)


# ── Upload ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="step-label">Step 1 — Upload Audio</div>', unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Drop audio file(s) here",
    type=["mp3", "m4a", "wav", "ogg"],
    accept_multiple_files=True,
    help="Upload 1–5 files in order. Each is transcribed sequentially."
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.warning("⚠️ Maximum 5 files at a time.")
        st.stop()

    total_mb = sum(f.size for f in uploaded_files) / (1024 * 1024)
    pills = "".join(
        f'<span class="file-pill">📁 {f.name} · {f.size/(1024*1024):.1f}MB</span>'
        for f in uploaded_files
    )
    st.markdown(
        f"{pills}<br/><small style='color:#444'>"
        f"{len(uploaded_files)} file(s) · {total_mb:.1f} MB total</small>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    # ── Discourse Context ──────────────────────────────────────────────────────
    st.markdown('<div class="step-label">Step 2 — Discourse Details (Optional)</div>', unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.83rem; color:#888; margin-bottom:0.6rem;'>"
        "Providing these details improves the insights panel and summary accuracy. "
        "Leave blank if unknown."
        "</div>",
        unsafe_allow_html=True
    )
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        speaker_hint = st.text_input(
            "🎙️ Speaker name",
            placeholder="e.g. Swami Tejomayananda",
            key="audio_speaker"
        )
    with dc2:
        topic_hint = st.text_input(
            "📖 Topic / Title",
            placeholder="e.g. Nature of the Atman",
            key="audio_topic"
        )
    with dc3:
        scripture_hint = st.text_input(
            "📚 Scripture / Text",
            placeholder="e.g. Bhagavad Gita Chapter 2",
            key="audio_scripture"
        )
    st.markdown("---")

    # ── Options ────────────────────────────────────────────────────────────────
    st.markdown('<div class="step-label">Step 3 — Output Options</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        summary_style = st.selectbox(
            "Summary style",
            ["Bullet highlights", "Main takeaways", "Detailed paragraphs",
             "Executive brief", "Academic digest", "Structured table"],
        )
    with col2:
        output_language = st.selectbox(
            "Output language", list(LANGUAGES.keys()), key="audio_lang"
        )
        # Clear old results if language changed
        if st.session_state.get("_audio_lang_prev") != output_language:
            st.session_state["_audio_lang_prev"] = output_language
            if "audio_results" in st.session_state:
                del st.session_state["audio_results"]

    selected_columns = []
    if summary_style == "Structured table":
        st.markdown("**Select table columns:**")
        cols = list(TABLE_COLUMNS.keys())
        selected_columns = st.multiselect(
            "Choose columns to include", cols, default=cols
        )
        if not selected_columns:
            st.warning("Please select at least one column.")

    analyze = st.checkbox(
        "🔍 Identify speaker, topic & scripture references", value=True
    )
    show_transcript = st.checkbox("Show full transcript on page", value=False)
    st.markdown("---")

    if not anthropic_key or not openai_key:
        st.warning("⚠️ Please enter both API keys in the sidebar.")
        st.stop()

    # ── Process ────────────────────────────────────────────────────────────────
    st.markdown('<div class="step-label">Step 4 — Process</div>', unsafe_allow_html=True)
    show_usage_badge()

    if st.button("🚀 Transcribe & Summarize", key="audio_process"):
        if not check_usage_limit():
            st.stop()
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.markdown("**Preparing audio chunks…**")
            progress_bar.progress(0.03)
            chunks = prepare_audio_chunks(uploaded_files)

            transcript = transcribe_chunks(
                chunks, openai_key, progress_bar, status_text
            )
            progress_bar.progress(0.70)

            # Analyze discourse
            insights = {}
            if analyze:
                status_text.markdown("**Analyzing discourse insights…**")
                insights = analyze_discourse(
                    transcript, anthropic_key,
                    speaker_hint=st.session_state.get("audio_speaker", ""),
                    topic_hint=st.session_state.get("audio_topic", ""),
                    scripture_hint=st.session_state.get("audio_scripture", "")
                )
                progress_bar.progress(0.78)

            status_text.markdown("**Summarizing with Claude…**")
            summary = summarize_text(
                transcript, summary_style, selected_columns, anthropic_key
            )
            progress_bar.progress(0.90)

            target_lang = LANGUAGES.get(output_language)
            if target_lang:
                status_text.markdown(f"**Translating to {target_lang}…**")
                summary = translate_text(summary, target_lang, anthropic_key)
                transcript = translate_text(transcript, target_lang, anthropic_key)

            progress_bar.progress(1.0)
            status_text.markdown("✅ **Done!**")
            increment_usage()

            # Store in session state so downloads don't clear results
            st.session_state["audio_results"] = {
                "summary": summary,
                "transcript": transcript,
                "insights": insights,
                "summary_style": summary_style,
                "show_transcript": show_transcript,
            }

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ── Show results persistently from session state ───────────────────────────────
if "audio_results" in st.session_state:
    r = st.session_state["audio_results"]
    summary = r["summary"]
    transcript = r["transcript"]
    insights = r["insights"]
    s_style = r["summary_style"]
    show_tr = r["show_transcript"]
    title = "Discourse Summary"

    st.markdown("---")
    st.markdown('<div class="step-label">Results</div>', unsafe_allow_html=True)

    # ── Discourse Header Block ─────────────────────────────────────────────────
    speaker_val = st.session_state.get("audio_speaker", "")
    topic_val = st.session_state.get("audio_topic", "")
    scripture_val = st.session_state.get("audio_scripture", "")
    lang_val = st.session_state.get("audio_lang", "English (default)")

    if any([speaker_val, topic_val, scripture_val]):
        header_html = (
            "<div style='background:#111; border:1px solid #2a2a2a;"
            " border-top:3px solid #c9a96e; border-radius:12px;"
            " padding:1.2rem 1.8rem; margin-bottom:1.2rem;'>"
            "<div style='display:grid; grid-template-columns:repeat(auto-fit, minmax(180px,1fr));"
            " gap:0.8rem;'>"
        )
        if speaker_val:
            header_html += (
                "<div>"
                "<div style='font-size:0.72rem; color:#666; text-transform:uppercase;"
                " letter-spacing:0.8px; margin-bottom:3px;'>🎙️ Speaker</div>"
                f"<div style='font-family:Cormorant Garamond,serif; font-size:1.15rem;"
                f" font-weight:700; color:#e8e0d4;'>{speaker_val}</div>"
                "</div>"
            )
        if topic_val:
            header_html += (
                "<div>"
                "<div style='font-size:0.72rem; color:#666; text-transform:uppercase;"
                " letter-spacing:0.8px; margin-bottom:3px;'>📖 Topic</div>"
                f"<div style='font-family:Cormorant Garamond,serif; font-size:1.15rem;"
                f" font-weight:700; color:#e8e0d4;'>{topic_val}</div>"
                "</div>"
            )
        if scripture_val:
            header_html += (
                "<div>"
                "<div style='font-size:0.72rem; color:#666; text-transform:uppercase;"
                " letter-spacing:0.8px; margin-bottom:3px;'>📚 Scripture</div>"
                f"<div style='font-family:Cormorant Garamond,serif; font-size:1.15rem;"
                f" font-weight:700; color:#c9a96e;'>{scripture_val}</div>"
                "</div>"
            )
        if lang_val and lang_val != "English (default)":
            header_html += (
                "<div>"
                "<div style='font-size:0.72rem; color:#666; text-transform:uppercase;"
                " letter-spacing:0.8px; margin-bottom:3px;'>🌐 Language</div>"
                f"<div style='font-family:Cormorant Garamond,serif; font-size:1.15rem;"
                f" font-weight:700; color:#e8e0d4;'>{lang_val}</div>"
                "</div>"
            )
        header_html += "</div></div>"
        st.markdown(header_html, unsafe_allow_html=True)

    # Insights panel
    if insights:
        show_insights(insights)

    # Summary
    st.markdown("#### 📝 Summary")
    if s_style == "Structured table":
        st.markdown(TABLE_CSS, unsafe_allow_html=True)
        st.markdown(markdown_table_to_html(summary), unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="output-box">{summary}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # All downloads — persistent
    show_downloads(title, summary, transcript, None)

    if show_tr:
        st.markdown("---")
        st.markdown("#### 📄 Full Transcript")
        st.markdown(
            f'<div class="output-box">{transcript}</div>',
            unsafe_allow_html=True
        )

    st.markdown(" ")
    if st.button("🔄 Clear results and start over", key="audio_clear"):
        del st.session_state["audio_results"]
        st.rerun()

