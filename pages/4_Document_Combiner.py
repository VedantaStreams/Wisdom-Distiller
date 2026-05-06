

def show_discourse_header(r):
    sp = r.get("speaker", "") or "—"
    tp = r.get("topic", "") or "—"
    sc = r.get("scripture", "") or "—"
    lg = r.get("language", "English (default)") or "English (default)"
    st.markdown(f"""
<div style="background:#111;border:1px solid #2a2a2a;border-top:4px solid #c9a96e;
            border-radius:12px;padding:1.4rem 2rem;margin-bottom:1.5rem;">
  <div style="font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
              letter-spacing:1px;font-weight:600;margin-bottom:1rem;">
    ✦ Discourse Details
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1.2rem;">
    <div>
      <div style="font-size:0.7rem;color:#666;margin-bottom:4px;">🎙️ SPEAKER</div>
      <div style="font-size:1.1rem;font-weight:700;color:#e8e0d4;">{sp}</div>
    </div>
    <div>
      <div style="font-size:0.7rem;color:#666;margin-bottom:4px;">📖 TOPIC</div>
      <div style="font-size:1.1rem;font-weight:700;color:#e8e0d4;">{tp}</div>
    </div>
    <div>
      <div style="font-size:0.7rem;color:#666;margin-bottom:4px;">📚 SCRIPTURE</div>
      <div style="font-size:1.1rem;font-weight:700;color:#c9a96e;">{sc}</div>
    </div>
    <div>
      <div style="font-size:0.7rem;color:#666;margin-bottom:4px;">🌐 LANGUAGE</div>
      <div style="font-size:1.1rem;font-weight:700;color:#e8e0d4;">{lg}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
import streamlit as st
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.styles import SHARED_CSS
from utils.helpers import summarize_text, translate_text, make_pdf, make_docx, TABLE_COLUMNS, markdown_table_to_html, TABLE_CSS, LANGUAGES

st.set_page_config(page_title="Document Combiner · Wisdom Distiller", page_icon="📄", layout="centered")
st.markdown(SHARED_CSS, unsafe_allow_html=True)

anthropic_key = st.session_state.get("anthropic_key", "")
if not anthropic_key:
    try: anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
    except: pass

st.markdown("""
<div class="hero">
    <h1>📄 Document <span class="accent">Combiner</span></h1>
    <p class="subtitle">Upload multiple transcripts · Merge into one unified document · Export as PDF or Word</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="about-box">
    Have multiple transcripts or summaries saved as <b>.txt files</b>? Upload them here in the correct
    order — the app will merge them into a single cohesive document and optionally re-summarize the
    combined content. Export the final result as <b>PDF or DOCX</b>.
</div>
""", unsafe_allow_html=True)

# ── Upload ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="step-label">Step 1 — Upload Transcripts</div>', unsafe_allow_html=True)
uploaded_txts = st.file_uploader(
    "Upload .txt transcript files",
    type=["txt"],
    accept_multiple_files=True,
    help="Upload transcript .txt files in the order they should be combined."
)

if uploaded_txts:
    if len(uploaded_txts) > 10:
        st.warning("⚠️ Maximum 10 files at a time.")
        st.stop()

    pills = "".join(f'<span class="file-pill">📄 {f.name}</span>' for f in uploaded_txts)
    st.markdown(f"{pills}<br/><small style='color:#444'>{len(uploaded_txts)} file(s) uploaded</small>", unsafe_allow_html=True)

    # Read all files
    combined_text = ""
    for i, f in enumerate(uploaded_txts):
        content = f.read().decode("utf-8", errors="ignore").strip()
        combined_text += f"\n\n--- Part {i+1}: {f.name} ---\n\n{content}"

    st.markdown("---")
    st.markdown('<div class="step-label">Step 2 — Options</div>', unsafe_allow_html=True)

    mode = st.radio(
        "What would you like to do?",
        ["Merge only (no re-summarization)", "Merge & re-summarize into one document"],
        index=1
    )

    col1, col2 = st.columns(2)
    with col1:
        doc_title = st.text_input("Document title", value="Combined Discourse")
    with col2:
        output_format = st.selectbox("Download format", ["TXT", "PDF", "DOCX"])

    summary_style = None
    selected_columns = []

    if mode == "Merge & re-summarize into one document":
        summary_style = st.selectbox(
            "Summary style",
            ["Bullet highlights", "Main takeaways", "Detailed paragraphs",
             "Executive brief", "Academic digest", "Structured table"],
        )
        if summary_style == "Structured table":
            cols = list(TABLE_COLUMNS.keys())
            selected_columns = st.multiselect("Choose table columns", cols, default=cols)

    output_language = st.selectbox(
        "Output language",
        list(LANGUAGES.keys()),
        key="doc_lang"
    )
    st.markdown("---")
    if not anthropic_key and mode == "Merge & re-summarize into one document":
        st.warning("⚠️ Anthropic API key needed for re-summarization. Enter it on the main page sidebar.")
        st.stop()

    st.markdown('<div class="step-label">Step 3 — Generate</div>', unsafe_allow_html=True)
    if st.button("📄 Combine & Export"):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            if mode == "Merge only (no re-summarization)":
                final_content = combined_text.strip()
                status_text.markdown("✅ **Files merged!**")
                progress_bar.progress(1.0)
            else:
                status_text.markdown("**Sending combined transcript to Claude…**")
                progress_bar.progress(0.3)
                final_content = summarize_text(combined_text, summary_style, selected_columns, anthropic_key)
                progress_bar.progress(1.0)
                status_text.markdown("✅ **Done!**")

            st.markdown("---")
            st.markdown('<div class="step-label">Results</div>', unsafe_allow_html=True)
            # ── DISCOURSE HEADER ────────────────────────────────────────────────
            _sp = st.session_state.get("doc_speaker", "") or "—"
            _tp = st.session_state.get("doc_topic", "") or "—"
            _sc = st.session_state.get("doc_scripture", "") or "—"
            _lg = st.session_state.get("doc_lang", "English (default)") or "English (default)"
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


            st.markdown(f"#### 📄 {doc_title}")
            if summary_style == "Structured table":
                st.markdown(TABLE_CSS, unsafe_allow_html=True)
                st.markdown(markdown_table_to_html(final_content), unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="output-box">{final_content}</div>', unsafe_allow_html=True)

            st.markdown(" ")
            dc1, dc2, dc3 = st.columns(3)

            with dc1:
                st.download_button("⬇️ Download (.txt)", data=final_content,
                                   file_name=f"{doc_title.lower().replace(' ','_')}.txt",
                                   mime="text/plain")
            if output_format == "PDF":
                pdf_bytes = make_pdf(doc_title, final_content)
                with dc2:
                    st.download_button("⬇️ Download (.pdf)", data=pdf_bytes,
                                       file_name=f"{doc_title.lower().replace(' ','_')}.pdf",
                                       mime="application/pdf")
            if output_format == "DOCX":
                docx_bytes = make_docx(doc_title, final_content)
                with dc3:
                    st.download_button("⬇️ Download (.docx)", data=docx_bytes,
                                       file_name=f"{doc_title.lower().replace(' ','_')}.docx",
                                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        except Exception as e:
            st.error(f"❌ Error: {e}")
