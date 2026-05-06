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
    Upload a single long audio file <b>or</b> up to 5 shorter segments.
    Files are transcribed in the order uploaded and combined into one unified summary.
    Supports <b>MP3, M4A, WAV, OGG</b>.
</div>
""", unsafe_allow_html=True)


# ── Discourse header ───────────────────────────────────────────────────────────
def show_discourse_header(r):
    sp  = r.get("speaker", "") or "—"
    tp  = r.get("topic", "") or "—"
    sc  = r.get("scripture", "") or "—"
    lg  = r.get("language", "English (default)") or "English (default)"

    # Pull verses and key terms from insights
    insights = r.get("insights", {})
    verses   = insights.get("scriptures", [])
    terms    = insights.get("key_terms", [])
    verse_str = " · ".join(verses) if verses else "—"
    terms_str = " · ".join(terms)  if terms  else "—"

    # Top row — 4 columns
    st.markdown(
        "<div style='border-top:4px solid #c9a96e; margin-bottom:0.5rem;'></div>",
        unsafe_allow_html=True
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("**🎙️ Speaker**")
        st.markdown(f"**{sp}**")
    with c2:
        st.markdown("**📖 Topic**")
        st.markdown(f"**{tp}**")
    with c3:
        st.markdown("**📚 Scripture**")
        st.markdown(f"**{sc}**")
    with c4:
        st.markdown("**🌐 Language**")
        st.markdown(f"**{lg}**")

    # Second row — verses and key terms
    if verses or terms:
        st.markdown(
            f"<div style='background:#111; border:1px solid #2a2a2a; border-radius:8px;"
            f" padding:0.7rem 1.2rem; margin-top:0.3rem; margin-bottom:0.5rem;'>"
            f"<span style='font-size:0.72rem; color:#666; text-transform:uppercase;"
            f" letter-spacing:0.8px;'>📜 Verses Referenced</span>&nbsp;&nbsp;"
            f"<span style='font-size:0.85rem; color:#c9a96e;'>{verse_str}</span>"
            f"<br/>"
            f"<span style='font-size:0.72rem; color:#666; text-transform:uppercase;"
            f" letter-spacing:0.8px;'>🔑 Key Terms</span>&nbsp;&nbsp;"
            f"<span style='font-size:0.85rem; color:#b8a88a; font-style:italic;'>{terms_str}</span>"
            f"</div>",
            unsafe_allow_html=True
        )
    st.markdown("---")


# ── Insights panel ─────────────────────────────────────────────────────────────
def show_insights(insights):
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
        + (f"<div style='color:#666;'>📚 Scripture</div><div style='color:#e8e0d4;'>{scripture_text}</div>" if scripture_text else "")
        + f"<div style='color:#666;'>📜 Verses Referenced</div><div style='color:#c9a96e;'>{scripture_str}</div>"
        + f"<div style='color:#666;'>🔑 Key Terms</div><div style='color:#b8a88a; font-style:italic;'>{terms_str}</div>"
        + "</div></div>",
        unsafe_allow_html=True
    )


# ── Downloads ──────────────────────────────────────────────────────────────────
def show_downloads(title, summary, transcript, r=None):
    _sp = r.get("speaker","") if r else ""
    _tp = r.get("topic","") if r else ""
    _sc = r.get("scripture","") if r else ""
    _lg = r.get("language","English (default)") if r else ""
    _insights = r.get("insights", {}) if r else {}
    _verses = _insights.get("scriptures", [])
    _terms  = _insights.get("key_terms", [])
    st.markdown("#### ⬇️ Downloads")
    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:10px;"
        " padding:1rem 1.4rem; margin-bottom:0.5rem;'>"
        "<div style='font-size:0.8rem; color:#666; margin-bottom:0.6rem;'>Summary</div>",
        unsafe_allow_html=True
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("⬇️ TXT", data=summary,
                           file_name="summary.txt", mime="text/plain",
                           key="dl_sum_txt")
    with c2:
        st.download_button("⬇️ PDF", data=make_pdf(title, summary, speaker=_sp, topic=_tp, scripture=_sc, language=_lg, verses=_verses, key_terms=_terms),
                           file_name="summary.pdf", mime="application/pdf",
                           key="dl_sum_pdf")
    with c3:
        st.download_button("⬇️ DOCX", data=make_docx(title, summary),
                           file_name="summary.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           key="dl_sum_docx")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:10px;"
        " padding:1rem 1.4rem;'>"
        "<div style='font-size:0.8rem; color:#666; margin-bottom:0.6rem;'>Full Transcript</div>",
        unsafe_allow_html=True
    )
    t1, t2, t3 = st.columns(3)
    with t1:
        st.download_button("⬇️ TXT", data=transcript,
                           file_name="transcript.txt", mime="text/plain",
                           key="dl_tr_txt")
    with t2:
        st.download_button("⬇️ PDF", data=make_pdf(title + " — Transcript", transcript, speaker=_sp, topic=_tp, scripture=_sc, language=_lg, verses=_verses, key_terms=_terms),
                           file_name="transcript.pdf", mime="application/pdf",
                           key="dl_tr_pdf")
    with t3:
        st.download_button("⬇️ DOCX", data=make_docx(title + " — Transcript", transcript),
                           file_name="transcript.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           key="dl_tr_docx")
    st.markdown("</div>", unsafe_allow_html=True)


# ── Upload ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="step-label">Step 1 — Upload Audio</div>', unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Drop audio file(s) here",
    type=["mp3", "m4a", "wav", "ogg"],
    accept_multiple_files=True
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.warning("⚠️ Maximum 5 files.")
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

    # Step 2 — Discourse Details
    st.markdown('<div class="step-label">Step 2 — Discourse Details (Optional)</div>',
                unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.83rem; color:#888; margin-bottom:0.6rem;'>"
        "Speaker name cannot be auto-detected unless mentioned in the audio. "
        "Enter details here for accurate insights.</div>",
        unsafe_allow_html=True
    )
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        speaker_hint = st.text_input("🎙️ Speaker name",
                                     placeholder="e.g. Swami Tejomayananda",
                                     key="audio_speaker")
    with dc2:
        topic_hint = st.text_input("📖 Topic / Title",
                                   placeholder="e.g. Nature of the Atman",
                                   key="audio_topic")
    with dc3:
        scripture_hint = st.text_input("📚 Scripture / Text",
                                       placeholder="e.g. Mundaka Upanishad",
                                       key="audio_scripture")
    st.markdown("---")

    # Step 3 — Output Options
    st.markdown('<div class="step-label">Step 3 — Output Options</div>',
                unsafe_allow_html=True)
    with st.expander("📖 Guide to Output Formats — click to expand before choosing"):
        st.markdown("""
| Format | Best For | What You Get |
|---|---|---|
| **Bullet highlights** | Quick review | Key points as concise bullets |
| **Main takeaways** | Sharing with others | 5-7 top insights in plain language |
| **Detailed paragraphs** | Deep study | Full flowing summary with context |
| **Executive brief** | Busy readers | Short 1-page overview |
| **Academic digest** | Scholars | Structured analysis with references |
| **Structured table** | Note-taking | 4-column table: Main Point · Explanation · Example · Personal Reflection |
""")

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
        if st.session_state.get("_audio_lang_prev") != output_language:
            st.session_state["_audio_lang_prev"] = output_language
            if "audio_results" in st.session_state:
                del st.session_state["audio_results"]

    selected_columns = []
    if summary_style == "Structured table":
        st.markdown("**Select table columns:**")
        cols = list(TABLE_COLUMNS.keys())
        selected_columns = st.multiselect(
            "Choose columns", cols, default=cols
        )
        if not selected_columns:
            st.warning("Please select at least one column.")

    analyze = st.checkbox("🔍 Identify speaker, topic & scripture references", value=True)
    show_transcript = st.checkbox("Show full transcript on page", value=False)
    st.markdown("---")

    if not anthropic_key or not openai_key:
        st.warning("⚠️ Please enter both API keys in the sidebar.")
        st.stop()

    # Step 4 — Process
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
                chunks, openai_key, progress_bar, status_text,
                speaker=speaker_hint, scripture=scripture_hint
            )
            progress_bar.progress(0.70)

            insights = {}
            if analyze:
                status_text.markdown("**Analyzing discourse insights…**")
                insights = analyze_discourse(
                    transcript, anthropic_key,
                    speaker_hint=speaker_hint,
                    topic_hint=topic_hint,
                    scripture_hint=scripture_hint
                )
                progress_bar.progress(0.78)
                # Auto-fill missing fields from insights
                if not speaker_hint and insights.get("speaker", "Unknown") != "Unknown":
                    speaker_hint = insights.get("speaker", "")
                if not topic_hint and insights.get("topic", "Could not determine") != "Could not determine":
                    topic_hint = insights.get("topic", "")
                if not scripture_hint and insights.get("scripture_text", ""):
                    scripture_hint = insights.get("scripture_text", "")

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

            # Store everything including discourse details
            st.session_state["audio_results"] = {
                "speaker": speaker_hint,
                "topic": topic_hint,
                "scripture": scripture_hint,
                "language": output_language,
                "summary": summary,
                "transcript": transcript,
                "insights": insights,
                "summary_style": summary_style,
                "show_transcript": show_transcript,
            }

        except Exception as e:
            st.error(f"❌ Error: {e}")


# ── Results ────────────────────────────────────────────────────────────────────
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

    # ── DISCOURSE HEADER — always shows ───────────────────────────────────────
    show_discourse_header(r)

    # ── Insights panel ─────────────────────────────────────────────────────────
    if insights:
        show_insights(insights)

    # ── Summary ────────────────────────────────────────────────────────────────
    st.markdown("#### 📝 Summary")
    if s_style == "Structured table":
        st.markdown(TABLE_CSS, unsafe_allow_html=True)
        st.markdown(markdown_table_to_html(summary), unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="output-box">{summary}</div>', unsafe_allow_html=True)

    st.markdown("---")
    show_downloads(title, summary, transcript, r=r)

    if show_tr:
        st.markdown("---")
        st.markdown("#### 📄 Full Transcript")
        st.markdown(f'<div class="output-box">{transcript}</div>', unsafe_allow_html=True)

    st.markdown(" ")
    if st.button("🔄 Clear results and start over", key="audio_clear"):
        del st.session_state["audio_results"]
        st.rerun()

