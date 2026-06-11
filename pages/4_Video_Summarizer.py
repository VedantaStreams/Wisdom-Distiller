import streamlit as st
import sys
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="Video Summarizer · Wisdom Distiller",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils.styles import SHARED_CSS
from utils.helpers import (

    extract_audio_from_video,
    clean_youtube_url,
    split_audio_ffmpeg,
    transcribe_chunks,
    summarize_text,
    translate_text,
    make_pdf,
    make_docx,
    TABLE_COLUMNS,
    markdown_table_to_html,
    TABLE_CSS,
    LANGUAGES
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── Home button in sidebar ────────────────────────────────────────────────────
with st.sidebar:
    try:
        st.page_link("app.py", label="🏠 Home")
    except Exception:
        if st.button("🏠 Home", key="home_btn_" + __file__[-20:]):
            st.switch_page("app.py")
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🎬 Video <span class="accent">Summarizer</span></h1>
    <p class="subtitle">YouTube & MP4 · Transcribe · Summarize · Export</p>
</div>
""", unsafe_allow_html=True)

def show_discourse_header(r):
    sp  = r.get("speaker", "") or "—"
    tp  = r.get("topic", "") or "—"
    sc  = r.get("scripture", "") or "—"
    lg  = r.get("language", "English (default)") or "English (default)"
    insights = r.get("insights", {})
    verses   = insights.get("scriptures", [])
    terms    = insights.get("key_terms", [])
    verse_str = " · ".join(verses) if verses else "—"
    terms_str = " · ".join(terms)  if terms  else "—"
    verses_row = ""
    if verses or terms:
        verses_row = (
            f"<div style='border-top:1px solid #2a2a2a;padding:0.6rem 1.2rem;'>"
            f"<span style='font-size:0.7rem;color:#666;text-transform:uppercase;"
            f"letter-spacing:0.8px;'>📜 Verses Referenced</span>&nbsp;&nbsp;"
            f"<span style='font-size:0.85rem;color:#c9a96e;'>{verse_str}</span>"
            f"<br/>"
            f"<span style='font-size:0.7rem;color:#666;text-transform:uppercase;"
            f"letter-spacing:0.8px;'>🔑 Key Terms</span>&nbsp;&nbsp;"
            f"<span style='font-size:0.85rem;color:#b8a88a;font-style:italic;'>{terms_str}</span>"
            f"</div>"
        )
    st.markdown(
        f"<div style='background:#111;border:1px solid #2a2a2a;border-top:4px solid #c9a96e;"
        f"border-radius:12px;padding:1.4rem 2rem 0;margin-bottom:1.5rem;'>"
        f"<div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;"
        f"letter-spacing:1px;font-weight:600;margin-bottom:1rem;'>✦ Discourse Details</div>"
        f"<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:1.2rem;padding-bottom:1rem;'>"
        f"<div><div style='font-size:0.7rem;color:#666;margin-bottom:4px;'>🎙️ SPEAKER</div>"
        f"<div style='font-size:0.78rem;font-weight:700;color:#e8e0d4;'>{sp}</div></div>"
        f"<div><div style='font-size:0.7rem;color:#666;margin-bottom:4px;'>📖 TOPIC</div>"
        f"<div style='font-size:0.78rem;font-weight:700;color:#e8e0d4;'>{tp}</div></div>"
        f"<div><div style='font-size:0.7rem;color:#666;margin-bottom:4px;'>📚 SCRIPTURE</div>"
        f"<div style='font-size:0.78rem;font-weight:700;color:#c9a96e;'>{sc}</div></div>"
        f"<div><div style='font-size:0.7rem;color:#666;margin-bottom:4px;'>🌐 LANGUAGE</div>"
        f"<div style='font-size:0.78rem;font-weight:700;color:#e8e0d4;'>{lg}</div></div>"
        f"</div>"
        f"{verses_row}"
        f"</div>",
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# MAIN TABS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="step-label">Step 1 — Choose Input</div>', unsafe_allow_html=True)
tab_yt, tab_mp4 = st.tabs(["▶ YouTube Video", "📁 Upload MP4"])


# ══════════════════════════════════════════════════════════════════════════════
# YOUTUBE TAB
# ══════════════════════════════════════════════════════════════════════════════
with tab_yt:

    # ── How it works box ──────────────────────────────────────────────────────
    st.markdown("""
<div class="about-box">
    To summarize a YouTube discourse, extract the audio using
    <b>4K Video Downloader</b> (free) and upload the MP3 directly below.
    The full transcript and summary will appear on this page — no need to
    switch to the Audio Summarizer.
</div>
""", unsafe_allow_html=True)

    # ── 4K Downloader instructions card ───────────────────────────────────────
    st.markdown(
        "<div style='background:#111; border:1px solid #2a2a2a; border-radius:12px; padding:1.4rem 1.8rem; margin-bottom:1.2rem;'>"
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem; color:#c9a96e; font-weight:600; margin-bottom:0.8rem;'>"
        "&#x1F5A5;&#xFE0F; Step 1 &#8212; Download audio using 4K Video Downloader"
        "</div>"
        "<div style='font-size:0.84rem; color:#888; line-height:1.9;'>"
        "<b style='color:#b8a88a;'>1.</b> Download the free app from "
        "<a href='https://www.4kdownload.com/products/videodownloader' target='_blank' style='color:#c9a96e;'>4kdownload.com</a><br/>"
        "<b style='color:#b8a88a;'>2.</b> Open the app and click <b>Paste Link</b><br/>"
        "<b style='color:#b8a88a;'>3.</b> Select <b>Extract Audio</b>, Format: <b>MP3</b>, click <b>Download</b><br/>"
        "<b style='color:#b8a88a;'>4.</b> Upload the downloaded MP3 below"
        "</div>"
        "<div style='margin-top:0.8rem;'>"
        "<a href='https://www.4kdownload.com/products/videodownloader' target='_blank' "
        "style='display:inline-block; background:#c9a96e; color:#0a0a0a; font-size:0.82rem; font-weight:500; padding:0.4rem 1.2rem; border-radius:6px; text-decoration:none;'>"
        "Download 4K Video Downloader (Free)"
        "</a></div></div>",
        unsafe_allow_html=True
    )

    # ── URL cleaner ───────────────────────────────────────────────────────────
    st.markdown(
        "<div style='font-size:0.82rem; color:#666; margin-bottom:0.4rem;'>"
        "💡 Paste your YouTube URL below to get a clean link for 4K Downloader:"
        "</div>",
        unsafe_allow_html=True
    )

    raw_url = st.text_input(
        "Paste YouTube URL (optional — to get clean link)",
        placeholder="https://www.youtube.com/watch?v=...&list=...",
        key="yt_url_cleaner",
        label_visibility="collapsed"
    )
    if raw_url and raw_url.strip():
        cleaned = clean_youtube_url(raw_url.strip())
        st.success(f"✅ Clean URL — copy and paste into 4K Downloader: `{cleaned}`")

    st.markdown(" ")

    # ── Nested Audio Upload ────────────────────────────────────────────────────
    st.markdown(
        "<div style='font-family:Cormorant Garamond,serif; font-size:1.05rem; "
        "color:#c9a96e; font-weight:600; margin-bottom:0.5rem;'>"
        "🎵 Step 2 &#8212; Upload the downloaded MP3 here"
        "</div>",
        unsafe_allow_html=True
    )

    uploaded_mp3 = st.file_uploader(
        "Upload MP3 from 4K Video Downloader",
        type=["mp3", "m4a", "wav", "ogg"],
        accept_multiple_files=True,
        key="yt_mp3_upload",
        help="Upload 1 or more MP3 segments in order — they are transcribed sequentially."
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

        # Save all uploaded files to temp and merge
        tmp_dir = tempfile.mkdtemp()
        saved_paths = []
        for i, f in enumerate(uploaded_mp3):
            suffix = Path(f.name).suffix
            tmp_path = os.path.join(tmp_dir, f"yt_audio_{i+1}{suffix}")
            with open(tmp_path, "wb") as out:
                out.write(f.read())
            saved_paths.append(tmp_path)

        # If multiple files, concatenate using ffmpeg
        if len(saved_paths) == 1:
            st.session_state["video_audio_path"] = saved_paths[0]
        else:
            concat_list = os.path.join(tmp_dir, "concat.txt")
            with open(concat_list, "w") as cl:
                for p in saved_paths:
                    cl.write(f"file '{p}'\n")
            merged_path = os.path.join(tmp_dir, "merged_audio.mp3")
            import subprocess
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
    Upload an <b>MP4, MOV, MKV or WEBM</b> video file. Audio is extracted
    automatically using ffmpeg, then transcribed and summarized on this page.
</div>
""", unsafe_allow_html=True)

    video_file = st.file_uploader(
        "Upload video file",
        type=["mp4", "mov", "mkv", "webm"],
        key="mp4_upload",
        help="Audio extracted automatically using ffmpeg."
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
                    st.success(
                        f"✅ Audio extracted! ({size_mb:.1f} MB) — scroll down to transcribe."
                    )
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")


# ══════════════════════════════════════════════════════════════════════════════
# SHARED PIPELINE — appears once audio is ready from any source
# ══════════════════════════════════════════════════════════════════════════════
audio_ready_path = st.session_state.get("video_audio_path", "")
if audio_ready_path and os.path.exists(audio_ready_path):

    st.markdown("---")

    size_mb = os.path.getsize(audio_ready_path) / (1024 * 1024)
    st.markdown(f"""
<div style="background:#111; border:1px solid #2a2a2a; border-left:3px solid #c9a96e;
            border-radius:8px; padding:0.7rem 1.2rem; margin-bottom:1rem;">
    <span style="color:#c9a96e; font-size:0.85rem;">🎵 Audio ready</span>
    <span style="color:#555; font-size:0.8rem; margin-left:1rem;">{size_mb:.1f} MB</span>
    <span style="color:#444; font-size:0.8rem;"> · configure options below</span>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="step-label">Step 2 — Output Options</div>', unsafe_allow_html=True)

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
            key="vid_style"
        )
    with col2:
        output_format = st.selectbox(
            "Download format", ["TXT", "PDF", "DOCX"],
            key="vid_format"
        )

    selected_columns = []
    if summary_style == "Structured table":
        st.markdown("**Select table columns:**")
        cols = list(TABLE_COLUMNS.keys())
        selected_columns = st.multiselect(
            "Choose columns to include", cols, default=cols,
            key="vid_cols"
        )
        if not selected_columns:
            st.warning("Please select at least one column.")

    show_transcript = st.checkbox(
        "Show full transcript on page", value=False, key="vid_show_tr"
    )
    st.markdown("---")

    if not anthropic_key or not openai_key:
        st.warning("⚠️ Please enter both API keys in the sidebar.")
        st.stop()

    st.markdown(
        '<div class="step-label">Step 3 — Transcribe & Summarize</div>',
        unsafe_allow_html=True
    )

    if st.button("🚀 Transcribe & Summarize", key="vid_process"):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.markdown("**Preparing audio…**")
            progress_bar.progress(0.05)

            chunks = split_audio_ffmpeg(audio_ready_path)
            progress_bar.progress(0.15)

            transcript = transcribe_chunks(
                chunks, openai_key, progress_bar, status_text
            )
            progress_bar.progress(0.80)

            status_text.markdown("**Transcription done! Summarizing with Claude…**")
            summary = summarize_text(
                transcript, summary_style, selected_columns, anthropic_key
            )
            progress_bar.progress(1.0)
            status_text.markdown("✅ **Done!**")

            st.session_state.pop("video_audio_path", None)

            st.markdown("---")
            st.markdown(
                '<div class="step-label">Results</div>', unsafe_allow_html=True
            )

            # ── DISCOURSE HEADER ────────────────────────────────────────────────
            _sp = st.session_state.get("vid_speaker", "") or "—"
            _tp = st.session_state.get("vid_topic", "") or "—"
            _sc = st.session_state.get("vid_scripture", "") or "—"
            _lg = st.session_state.get("vid_lang", "English (default)") or "English (default)"
            st.markdown(
                "<div style='background:#111; border:1px solid #2a2a2a;"
                " border-top:4px solid #c9a96e; border-radius:12px;"
                " padding:1.4rem 2rem; margin-bottom:1.5rem;'>"
                "<div style='font-size:0.7rem; color:#c9a96e; text-transform:uppercase;"
                " letter-spacing:1px; font-weight:500; margin-bottom:1rem;'>Discourse Details</div>"
                "<div style='display:grid; grid-template-columns:repeat(4,1fr); gap:1.2rem;'>"
                "<div><div style='font-size:0.68rem; color:#555; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:5px;'>🎙️ Speaker</div>"
                f"<div style='font-family:Cormorant Garamond,serif; font-size:1.2rem; font-weight:700; color:#e8e0d4;'>{_sp}</div></div>"
                "<div><div style='font-size:0.68rem; color:#555; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:5px;'>📖 Topic</div>"
                f"<div style='font-family:Cormorant Garamond,serif; font-size:1.2rem; font-weight:700; color:#e8e0d4;'>{_tp}</div></div>"
                "<div><div style='font-size:0.68rem; color:#555; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:5px;'>📚 Scripture</div>"
                f"<div style='font-family:Cormorant Garamond,serif; font-size:1.2rem; font-weight:700; color:#c9a96e;'>{_sc}</div></div>"
                "<div><div style='font-size:0.68rem; color:#555; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:5px;'>🌐 Language</div>"
                f"<div style='font-family:Cormorant Garamond,serif; font-size:1.2rem; font-weight:700; color:#e8e0d4;'>{_lg}</div></div>"
                "</div></div>",
                unsafe_allow_html=True
            )

            # ── Transcript ─────────────────────────────────────────────────────
            st.markdown("#### 📄 Full Transcript")
            st.markdown(
                f'<div class="output-box">{transcript}</div>',
                unsafe_allow_html=True
            )
            st.download_button(
                "⬇️ Download Transcript (.txt)",
                data=transcript,
                file_name="transcript.txt",
                mime="text/plain",
                key="dl_transcript"
            )

            st.markdown("---")

            # ── Summary ────────────────────────────────────────────────────────
            st.markdown("#### 📝 Summary")
            if summary_style == "Structured table":
                st.markdown(TABLE_CSS, unsafe_allow_html=True)
                st.markdown(markdown_table_to_html(summary), unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="output-box">{summary}</div>',
                    unsafe_allow_html=True
                )

            st.markdown(" ")
            dc1, dc2, dc3 = st.columns(3)
            title = "Video Discourse Summary"

            with dc1:
                st.download_button(
                    "⬇️ Summary (.txt)", data=summary,
                    file_name="summary.txt", mime="text/plain",
                    key="dl_sum_txt"
                )
            if output_format == "PDF":
                pdf_bytes = make_pdf(title, summary)
                with dc2:
                    st.download_button(
                        "⬇️ Summary (.pdf)", data=pdf_bytes,
                        file_name="summary.pdf", mime="application/pdf",
                        key="dl_sum_pdf"
                    )
            if output_format == "DOCX":
                docx_bytes = make_docx(title, summary)
                with dc3:
                    st.download_button(
                        "⬇️ Summary (.docx)", data=docx_bytes,
                        file_name="summary.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        key="dl_sum_docx"
                    )

            if show_transcript:
                st.markdown("---")
                st.markdown("#### 📄 Full Transcript")
                st.markdown(
                    f'<div class="output-box">{transcript}</div>',
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
