import streamlit as st
import sys
import os
import tempfile
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.styles import SHARED_CSS
from utils.usage_tracker import check_usage_limit, increment_usage, show_usage_badge
from utils.helpers import (
    extract_audio_from_video,
    clean_youtube_url,
    split_audio_ffmpeg,
    transcribe_chunks,
    summarize_text,
    translate_text,
    analyze_discourse,
    make_pdf,
    make_docx,
    TABLE_COLUMNS,
    markdown_table_to_html,
    TABLE_CSS,
    LANGUAGES
)

st.set_page_config(
    page_title="Video Summarizer · Wisdom Distiller",
    page_icon="🎬",
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
    <h1>🎬 Video <span class="accent">Summarizer</span></h1>
    <p class="subtitle">YouTube or MP4 · Audio extracted · Transcribed · Summarized</p>
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
def show_downloads(title, summary, transcript):
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
                           key="vid_dl_sum_txt")
    with c2:
        st.download_button("⬇️ PDF", data=make_pdf(title, summary),
                           file_name="summary.pdf", mime="application/pdf",
                           key="vid_dl_sum_pdf")
    with c3:
        st.download_button("⬇️ DOCX", data=make_docx(title, summary),
                           file_name="summary.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           key="vid_dl_sum_docx")
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
                           key="vid_dl_tr_txt")
    with t2:
        st.download_button("⬇️ PDF", data=make_pdf(title + " — Transcript", transcript),
                           file_name="transcript.pdf", mime="application/pdf",
                           key="vid_dl_tr_pdf")
    with t3:
        st.download_button("⬇️ DOCX", data=make_docx(title + " — Transcript", transcript),
                           file_name="transcript.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           key="vid_dl_tr_docx")
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


# ══════════════════════════════════════════════════════════════════════════════
# MAIN TABS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="step-label">Step 1 — Choose Input</div>', unsafe_allow_html=True)
tab_yt, tab_mp4 = st.tabs(["▶ YouTube Video", "📁 Upload MP4"])


# ══════════════════════════════════════════════════════════════════════════════
# YOUTUBE TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_yt:
    st.markdown("""
<div class="about-box">
    Download audio from YouTube using <b>4K Video Downloader</b> (free),
    then upload the MP3 directly below. Full transcript and summary appear on this page.
</div>
""", unsafe_allow_html=True)

    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:12px;"
        " padding:1.2rem 1.6rem; margin-bottom:1rem;'>"
        "<div style='font-size:0.9rem; color:#c9a96e; font-weight:600; margin-bottom:0.6rem;'>"
        "🖥️ Download audio using 4K Video Downloader</div>"
        "<div style='font-size:0.83rem; color:#888; line-height:1.9;'>"
        "<b style='color:#b8a88a;'>1.</b> Download free from "
        "<a href='https://www.4kdownload.com/products/videodownloader' target='_blank'"
        " style='color:#c9a96e;'>4kdownload.com</a><br/>"
        "<b style='color:#b8a88a;'>2.</b> Open app → Paste Link → Extract Audio → MP3 → Download<br/>"
        "<b style='color:#b8a88a;'>3.</b> Upload the MP3 below ↓"
        "</div>"
        "<div style='margin-top:0.8rem;'>"
        "<a href='https://www.4kdownload.com/products/videodownloader' target='_blank'"
        " style='background:#c9a96e; color:#0a0a0a; padding:5px 14px; border-radius:6px;"
        " text-decoration:none; font-size:0.82rem; font-weight:500;'>"
        "Download 4K Video Downloader (Free)</a></div></div>",
        unsafe_allow_html=True
    )

    raw_url = st.text_input(
        "Paste YouTube URL to get a clean link",
        placeholder="https://www.youtube.com/watch?v=...&list=...",
        key="yt_url_cleaner", label_visibility="visible"
    )
    if raw_url and raw_url.strip():
        cleaned = clean_youtube_url(raw_url.strip())
        st.success(f"✅ Clean URL — copy into 4K Downloader: `{cleaned}`")

    st.markdown(" ")
    st.markdown(
        "<div style='font-size:0.85rem; color:#c9a96e; font-weight:500; margin-bottom:4px;'>"
        "🎵 Upload downloaded MP3 here</div>",
        unsafe_allow_html=True
    )
    uploaded_mp3 = st.file_uploader(
        "Upload MP3", type=["mp3", "m4a", "wav", "ogg"],
        accept_multiple_files=True, key="yt_mp3_upload"
    )

    if uploaded_mp3:
        total_mb = sum(f.size for f in uploaded_mp3) / (1024 * 1024)
        pills = "".join(
            f'<span class="file-pill">🎵 {f.name} · {f.size/(1024*1024):.1f} MB</span>'
            for f in uploaded_mp3
        )
        st.markdown(
            f"{pills}<br/><small style='color:#444'>"
            f"{len(uploaded_mp3)} file(s) · {total_mb:.1f} MB total</small>",
            unsafe_allow_html=True
        )
        tmp_dir = tempfile.mkdtemp()
        saved_paths = []
        for i, f in enumerate(uploaded_mp3):
            suffix = Path(f.name).suffix
            tmp_path = os.path.join(tmp_dir, f"yt_audio_{i+1}{suffix}")
            with open(tmp_path, "wb") as out:
                out.write(f.read())
            saved_paths.append(tmp_path)

        if len(saved_paths) == 1:
            st.session_state["video_audio_path"] = saved_paths[0]
        else:
            concat_list = os.path.join(tmp_dir, "concat.txt")
            with open(concat_list, "w") as cl:
                for p in saved_paths:
                    cl.write(f"file '{p}'\n")
            merged_path = os.path.join(tmp_dir, "merged_audio.mp3")
            subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                 "-i", concat_list, "-acodec", "copy", merged_path],
                capture_output=True
            )
            st.session_state["video_audio_path"] = merged_path
        st.success("✅ Audio ready — scroll down to transcribe.")


# ══════════════════════════════════════════════════════════════════════════════
# MP4 UPLOAD TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_mp4:
    st.markdown("""
<div class="about-box">
    Upload an <b>MP4, MOV, MKV or WEBM</b> video file.
    Audio is extracted automatically using ffmpeg.
</div>
""", unsafe_allow_html=True)

    video_file = st.file_uploader(
        "Upload video file", type=["mp4", "mov", "mkv", "webm"],
        key="mp4_upload"
    )
    if video_file:
        file_size_mb = video_file.size / (1024 * 1024)
        st.markdown(
            f'<span class="file-pill">🎬 {video_file.name} · {file_size_mb:.1f} MB</span>',
            unsafe_allow_html=True
        )
        if st.button("🎵 Extract Audio from Video", key="extract_mp4"):
            with st.spinner("Extracting audio…"):
                try:
                    tmp_dir = tempfile.mkdtemp()
                    suffix = Path(video_file.name).suffix
                    tmp_video = os.path.join(tmp_dir, f"video{suffix}")
                    with open(tmp_video, "wb") as f:
                        f.write(video_file.read())
                    extracted = extract_audio_from_video(tmp_video)
                    size_mb = os.path.getsize(extracted) / (1024 * 1024)
                    st.session_state["video_audio_path"] = extracted
                    st.success(f"✅ Audio extracted! ({size_mb:.1f} MB) — scroll down.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# ══════════════════════════════════════════════════════════════════════════════
# SHARED PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
audio_ready_path = st.session_state.get("video_audio_path", "")
if audio_ready_path and os.path.exists(audio_ready_path):

    st.markdown("---")
    size_mb = os.path.getsize(audio_ready_path) / (1024 * 1024)
    st.markdown(
        f"<div style='background:#111; border:1px solid #2a2a2a;"
        f" border-left:3px solid #c9a96e; border-radius:8px;"
        f" padding:0.7rem 1.2rem; margin-bottom:1rem;'>"
        f"<span style='color:#c9a96e; font-size:0.85rem;'>🎵 Audio ready</span>"
        f"<span style='color:#555; font-size:0.8rem; margin-left:1rem;'>{size_mb:.1f} MB</span>"
        f"<span style='color:#444; font-size:0.8rem;'> · configure below</span></div>",
        unsafe_allow_html=True
    )

    # ── Discourse Details ──────────────────────────────────────────────────────
    st.markdown('<div class="step-label">Step 2 — Discourse Details (Optional)</div>',
                unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.83rem; color:#888; margin-bottom:0.6rem;'>"
        "Providing these details improves insights accuracy. Leave blank if unknown."
        "</div>",
        unsafe_allow_html=True
    )
    vc1, vc2, vc3 = st.columns(3)
    with vc1:
        speaker_hint = st.text_input("🎙️ Speaker name",
                                     placeholder="e.g. Swami Tejomayananda  ← required for insights",
                                     key="vid_speaker")
    with vc2:
        topic_hint = st.text_input("📖 Topic / Title",
                                   placeholder="e.g. Nature of the Atman",
                                   key="vid_topic")
    with vc3:
        scripture_hint = st.text_input("📚 Scripture / Text",
                                       placeholder="e.g. Bhagavad Gita Chapter 2",
                                       key="vid_scripture")
    st.markdown("---")

    # ── Output Options ─────────────────────────────────────────────────────────
    st.markdown('<div class="step-label">Step 3 — Output Options</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        summary_style = st.selectbox(
            "Summary style",
            ["Bullet highlights", "Main takeaways", "Detailed paragraphs",
             "Executive brief", "Academic digest", "Structured table"],
            key="vid_style"
        )
    with col2:
        output_language = st.selectbox(
            "Output language", list(LANGUAGES.keys()), key="vid_lang"
        )
        # Clear old results if language changed
        if st.session_state.get("_vid_lang_prev") != output_language:
            st.session_state["_vid_lang_prev"] = output_language
            if "video_results" in st.session_state:
                del st.session_state["video_results"]

    selected_columns = []
    if summary_style == "Structured table":
        st.markdown("**Select table columns:**")
        cols = list(TABLE_COLUMNS.keys())
        selected_columns = st.multiselect(
            "Choose columns to include", cols, default=cols, key="vid_cols"
        )
        if not selected_columns:
            st.warning("Please select at least one column.")

    analyze = st.checkbox(
        "🔍 Identify speaker, topic & scripture references",
        value=True, key="vid_analyze"
    )
    show_transcript = st.checkbox(
        "Show full transcript on page", value=False, key="vid_show_tr"
    )
    st.markdown("---")

    if not anthropic_key or not openai_key:
        st.warning("⚠️ Please enter both API keys in the sidebar.")
        st.stop()

    # ── Process ────────────────────────────────────────────────────────────────
    st.markdown('<div class="step-label">Step 4 — Transcribe & Summarize</div>',
                unsafe_allow_html=True)
    show_usage_badge()

    if st.button("🚀 Transcribe & Summarize", key="vid_process"):
        if not check_usage_limit():
            st.stop()
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.markdown("**Preparing audio…**")
            progress_bar.progress(0.05)
            chunks = split_audio_ffmpeg(audio_ready_path)
            progress_bar.progress(0.15)

            transcript = transcribe_chunks(chunks, openai_key, progress_bar, status_text)
            progress_bar.progress(0.70)

            insights = {}
            if analyze:
                status_text.markdown("**Analyzing discourse insights…**")
                insights = analyze_discourse(
                    transcript, anthropic_key,
                    speaker_hint=st.session_state.get("vid_speaker", ""),
                    topic_hint=st.session_state.get("vid_topic", ""),
                    scripture_hint=st.session_state.get("vid_scripture", "")
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

            st.session_state.pop("video_audio_path", None)
            st.session_state["video_results"] = {
                "summary": summary,
                "transcript": transcript,
                "insights": insights,
                "summary_style": summary_style,
                "show_transcript": show_transcript,
            }

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


# ── Show results persistently ──────────────────────────────────────────────────
if "video_results" in st.session_state:
    r = st.session_state["video_results"]
    summary = r["summary"]
    transcript = r["transcript"]
    insights = r["insights"]
    s_style = r["summary_style"]
    show_tr = r["show_transcript"]
    title = "Video Discourse Summary"

    st.markdown("---")
    st.markdown('<div class="step-label">Results</div>', unsafe_allow_html=True)

    show_discourse_header("vid_speaker", "vid_topic", "vid_scripture", "vid_lang")

    if insights:
        show_insights(insights)

    st.markdown("#### 📝 Summary")
    if s_style == "Structured table":
        st.markdown(TABLE_CSS, unsafe_allow_html=True)
        st.markdown(markdown_table_to_html(summary), unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="output-box">{summary}</div>', unsafe_allow_html=True)

    st.markdown("---")
    show_downloads(title, summary, transcript)

    if show_tr:
        st.markdown("---")
        st.markdown("#### 📄 Full Transcript")
        st.markdown(f'<div class="output-box">{transcript}</div>', unsafe_allow_html=True)

    st.markdown(" ")
    if st.button("🔄 Clear results and start over", key="vid_clear"):
        del st.session_state["video_results"]
        st.rerun()

