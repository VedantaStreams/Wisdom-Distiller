import streamlit as st
import sys
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.styles import SHARED_CSS
from utils.usage_tracker import check_usage_limit, increment_usage, show_usage_badge
from utils.helpers import (
    summarize_text, translate_text, analyze_discourse,
    make_pdf, make_docx,
    TABLE_COLUMNS, markdown_table_to_html, TABLE_CSS, LANGUAGES
)

st.set_page_config(
    page_title="Document Combiner · Wisdom Distiller",
    page_icon="📄",
    layout="centered"
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


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>📄 Document <span class="accent">Combiner</span></h1>
    <p class="subtitle">Merge multiple transcripts · Re-summarize · Export</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="about-box">
    Upload multiple <b>.txt</b> transcript files — they are merged in order and
    either combined into one document or re-summarized into a unified summary.
    Ideal for combining transcripts from multiple discourse sessions.
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


# ── Helper: persistent downloads ───────────────────────────────────────────────
def show_downloads(title, content, label="Document"):
    st.markdown("#### ⬇️ Downloads")
    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:10px;"
        f" padding:1rem 1.4rem;'>"
        f"<div style='font-size:0.8rem; color:#666; margin-bottom:0.6rem;'>{label}</div>",
        unsafe_allow_html=True
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("⬇️ TXT", data=content,
                           file_name="document.txt", mime="text/plain",
                           key="doc_dl_txt")
    with c2:
        st.download_button("⬇️ PDF", data=make_pdf(title, content),
                           file_name="document.pdf", mime="application/pdf",
                           key="doc_dl_pdf")
    with c3:
        st.download_button("⬇️ DOCX", data=make_docx(title, content),
                           file_name="document.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           key="doc_dl_docx")
    st.markdown("</div>", unsafe_allow_html=True)


def show_discourse_header(speaker_key, topic_key, scripture_key, lang_key):
    """Show a bold discourse details header block above results."""
    speaker_val = st.session_state.get(speaker_key, "")
    topic_val = st.session_state.get(topic_key, "")
    scripture_val = st.session_state.get(scripture_key, "")
    lang_val = st.session_state.get(lang_key, "English (default)")

    if not any([speaker_val, topic_val, scripture_val]):
        return

    html = (
        "<div style='background:#111; border:1px solid #2a2a2a;"
        " border-top:3px solid #c9a96e; border-radius:12px;"
        " padding:1.2rem 1.8rem; margin-bottom:1.2rem;'>"
        "<div style='display:grid; grid-template-columns:repeat(auto-fit, minmax(180px,1fr));"
        " gap:0.8rem;'>"
    )
    if speaker_val:
        html += (
            "<div>"
            "<div style='font-size:0.72rem; color:#666; text-transform:uppercase;"
            " letter-spacing:0.8px; margin-bottom:3px;'>🎙️ Speaker</div>"
            f"<div style='font-family:Cormorant Garamond,serif; font-size:1.15rem;"
            f" font-weight:700; color:#e8e0d4;'>{speaker_val}</div>"
            "</div>"
        )
    if topic_val:
        html += (
            "<div>"
            "<div style='font-size:0.72rem; color:#666; text-transform:uppercase;"
            " letter-spacing:0.8px; margin-bottom:3px;'>📖 Topic</div>"
            f"<div style='font-family:Cormorant Garamond,serif; font-size:1.15rem;"
            f" font-weight:700; color:#e8e0d4;'>{topic_val}</div>"
            "</div>"
        )
    if scripture_val:
        html += (
            "<div>"
            "<div style='font-size:0.72rem; color:#666; text-transform:uppercase;"
            " letter-spacing:0.8px; margin-bottom:3px;'>📚 Scripture</div>"
            f"<div style='font-family:Cormorant Garamond,serif; font-size:1.15rem;"
            f" font-weight:700; color:#c9a96e;'>{scripture_val}</div>"
            "</div>"
        )
    if lang_val and lang_val != "English (default)":
        html += (
            "<div>"
            "<div style='font-size:0.72rem; color:#666; text-transform:uppercase;"
            " letter-spacing:0.8px; margin-bottom:3px;'>🌐 Language</div>"
            f"<div style='font-family:Cormorant Garamond,serif; font-size:1.15rem;"
            f" font-weight:700; color:#e8e0d4;'>{lang_val}</div>"
            "</div>"
        )
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)


# ── Upload ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="step-label">Step 1 — Upload Transcripts</div>',
            unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Upload .txt transcript files",
    type=["txt"],
    accept_multiple_files=True,
    help="Upload transcripts in the order they should be merged."
)

if uploaded_files:
    total_size = sum(f.size for f in uploaded_files)
    pills = "".join(
        f'<span class="file-pill">📄 {f.name} · {f.size/1024:.1f}KB</span>'
        for f in uploaded_files
    )
    st.markdown(
        f"{pills}<br/><small style='color:#444'>"
        f"{len(uploaded_files)} file(s) · {total_size/1024:.1f} KB total</small>",
        unsafe_allow_html=True
    )

    # Read all files
    combined_text = ""
    for f in uploaded_files:
        text = f.read().decode("utf-8", errors="ignore").strip()
        combined_text += f"\n\n{'='*60}\n{f.name}\n{'='*60}\n{text}"
    combined_text = combined_text.strip()

    st.markdown("---")

    # ── Discourse Details ──────────────────────────────────────────────────────
    st.markdown('<div class="step-label">Step 2 — Discourse Details (Optional)</div>',
                unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.83rem; color:#888; margin-bottom:0.6rem;'>"
        "Speaker name cannot be auto-detected unless mentioned in the audio. Please enter details here for accurate insights."
        "</div>",
        unsafe_allow_html=True
    )
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        speaker_hint = st.text_input("🎙️ Speaker name",
                                     placeholder="e.g. Swami Tejomayananda  ← required for insights",
                                     key="doc_speaker")
    with dc2:
        topic_hint = st.text_input("📖 Topic / Title",
                                   placeholder="e.g. Nature of the Atman",
                                   key="doc_topic")
    with dc3:
        scripture_hint = st.text_input("📚 Scripture / Text",
                                       placeholder="e.g. Bhagavad Gita Chapter 2",
                                       key="doc_scripture")
    st.markdown("---")

    # ── Options ────────────────────────────────────────────────────────────────
    st.markdown('<div class="step-label">Step 3 — Output Options</div>',
                unsafe_allow_html=True)

    mode = st.radio(
        "What would you like to do?",
        ["Merge & re-summarize into one document",
         "Merge only (combine transcripts as-is)"],
        horizontal=True
    )

    col1, col2 = st.columns(2)
    if mode == "Merge & re-summarize into one document":
        with col1:
            summary_style = st.selectbox(
                "Summary style",
                ["Bullet highlights", "Main takeaways", "Detailed paragraphs",
                 "Executive brief", "Academic digest", "Structured table"],
                key="doc_style"
            )
        with col2:
            output_language = st.selectbox(
                "Output language", list(LANGUAGES.keys()), key="doc_lang"
            )
            # Clear old results if language changed
            if st.session_state.get("_doc_lang_prev") != output_language:
                st.session_state["_doc_lang_prev"] = output_language
                if "doc_results" in st.session_state:
                    del st.session_state["doc_results"]

        selected_columns = []
        if summary_style == "Structured table":
            st.markdown("**Select table columns:**")
            cols = list(TABLE_COLUMNS.keys())
            selected_columns = st.multiselect(
                "Choose columns to include", cols, default=cols, key="doc_cols"
            )
            if not selected_columns:
                st.warning("Please select at least one column.")
    else:
        summary_style = None
        output_language = "English (default)"

    analyze = st.checkbox(
        "🔍 Identify speaker, topic & scripture references",
        value=True, key="doc_analyze"
    )
    st.markdown("---")

    if not anthropic_key:
        st.warning("⚠️ Please enter your Anthropic API key in the sidebar.")
        st.stop()

    # ── Process ────────────────────────────────────────────────────────────────
    st.markdown('<div class="step-label">Step 4 — Process</div>',
                unsafe_allow_html=True)
    show_usage_badge()

    if st.button("📄 Combine & Export", key="doc_process"):
        if not check_usage_limit():
            st.stop()
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.markdown("**Merging documents…**")
            progress_bar.progress(0.1)

            insights = {}
            final_content = combined_text

            if analyze:
                status_text.markdown("**Analyzing discourse insights…**")
                insights = analyze_discourse(
                    combined_text[:8000], anthropic_key,
                    speaker_hint=st.session_state.get("doc_speaker", ""),
                    topic_hint=st.session_state.get("doc_topic", ""),
                    scripture_hint=st.session_state.get("doc_scripture", "")
                )
                progress_bar.progress(0.35)

            if mode == "Merge & re-summarize into one document":
                status_text.markdown("**Summarizing with Claude…**")
                final_content = summarize_text(
                    combined_text, summary_style, selected_columns, anthropic_key
                )
                progress_bar.progress(0.80)

                target_lang = LANGUAGES.get(output_language)
                if target_lang:
                    status_text.markdown(f"**Translating to {target_lang}…**")
                    final_content = translate_text(
                        final_content, target_lang, anthropic_key
                    )

            progress_bar.progress(1.0)
            status_text.markdown("✅ **Done!**")
            increment_usage()

            st.session_state["doc_results"] = {
                "speaker": st.session_state.get("doc_speaker", ""),
                "topic": st.session_state.get("doc_topic", ""),
                "scripture": st.session_state.get("doc_scripture", ""),
                "language": st.session_state.get("doc_lang", "English (default)"),

                "content": final_content,
                "insights": insights,
                "summary_style": summary_style,
                "mode": mode,
            }

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


# ── Show results persistently ──────────────────────────────────────────────────
if "doc_results" in st.session_state:
    r = st.session_state["doc_results"]
    content = r["content"]
    insights = r["insights"]
    s_style = r["summary_style"]
    mode = r["mode"]
    title = "Combined Discourse Document"

    st.markdown("---")
    st.markdown('<div class="step-label">Results</div>', unsafe_allow_html=True)

    # Show header from stored results
    _sp = r.get("speaker", "")
    _tp = r.get("topic", "")
    _sc = r.get("scripture", "")
    _lg = r.get("language", "English (default)")
    if any([_sp, _tp, _sc]):
        _h = ("<div style='background:#111; border:1px solid #2a2a2a;"
              " border-top:3px solid #c9a96e; border-radius:12px;"
              " padding:1.2rem 1.8rem; margin-bottom:1.2rem;'>"
              "<div style='display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:0.8rem;'>"
        )
        if _sp: _h += (f"<div><div style='font-size:0.72rem;color:#666;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:3px;'>🎙️ Speaker</div>"
                       f"<div style='font-family:Cormorant Garamond,serif;font-size:1.15rem;font-weight:700;color:#e8e0d4;'>{_sp}</div></div>")
        if _tp: _h += (f"<div><div style='font-size:0.72rem;color:#666;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:3px;'>📖 Topic</div>"
                       f"<div style='font-family:Cormorant Garamond,serif;font-size:1.15rem;font-weight:700;color:#e8e0d4;'>{_tp}</div></div>")
        if _sc: _h += (f"<div><div style='font-size:0.72rem;color:#666;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:3px;'>📚 Scripture</div>"
                       f"<div style='font-family:Cormorant Garamond,serif;font-size:1.15rem;font-weight:700;color:#c9a96e;'>{_sc}</div></div>")
        if _lg and _lg != "English (default)": _h += (f"<div><div style='font-size:0.72rem;color:#666;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:3px;'>🌐 Language</div>"
                       f"<div style='font-family:Cormorant Garamond,serif;font-size:1.15rem;font-weight:700;color:#e8e0d4;'>{_lg}</div></div>")
        _h += "</div></div>"
        st.markdown(_h, unsafe_allow_html=True)

    if insights:
        show_insights(insights)

    label = "Summary" if mode == "Merge & re-summarize into one document" else "Combined Transcript"
    st.markdown(f"#### 📝 {label}")

    if s_style == "Structured table":
        st.markdown(TABLE_CSS, unsafe_allow_html=True)
        st.markdown(markdown_table_to_html(content), unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="output-box">{content}</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    show_downloads(title, content, label=label)

    st.markdown(" ")
    if st.button("🔄 Clear results and start over", key="doc_clear"):
        del st.session_state["doc_results"]
        st.rerun()
