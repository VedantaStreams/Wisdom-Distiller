import streamlit as st
import sys
import json
import re
import tempfile
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="Wisdom Extractor · Wisdom Distiller",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils.styles import SHARED_CSS
from utils.helpers import (
    make_pdf, make_docx, LANGUAGES,
    split_audio_ffmpeg, transcribe_chunks
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.page_link("app.py", label="🏠 Home")
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>💎 Wisdom <span class="accent">Extractor</span></h1>
    <p class="subtitle">Verbatim quotes · YouTube titles · Reels · Hashtags</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="about-box">
    Upload an audio file <b style='color:#b8a88a;'>or</b> paste a transcript.
    The AI extracts the most profound verbatim quotes, generates a YouTube title,
    reel caption, main takeaway, and hashtags — ready to publish.
    Sanskrit verses are always preserved in <b style='color:#c9a96e;'>Devanāgarī script</b>.
</div>
""", unsafe_allow_html=True)

# ── Extraction prompt ─────────────────────────────────────────────────────────
EXTRACTOR_PROMPT = """You are an expert curator of Vedantic discourses with specialization in:
- Verbatim wisdom extraction
- Vedantic thematic understanding
- Structured metadata generation
- High-quality content asset generation for YouTube, reels, and social media

Your objective is to extract the most profound teachings while preserving the exact spoken words of the teacher.

CRITICAL SANSKRIT RULE: Any Sanskrit verse, shloka, or mantra MUST be displayed in
Devanāgarī script ONLY (e.g. श्रेयान्स्वधर्मो विगुणः, ॐ तत् सत्).
Do NOT transliterate Sanskrit verses into Roman/English script under any circumstances.
After the Devanāgarī, you may provide the meaning in English.
For Swamiji names, use proper transliteration (e.g. Swami Aparājitānandajī, Swāmī Śaraṇānandajī).

==================================================================
PART 1 — METADATA EXTRACTION
==================================================================
From the discourse, identify:
1. Speaker Name (with proper transliteration)
2. Topic / Main Theme
3. Referenced Scriptural Text (e.g. Bhagavad Gītā, Upaniṣads, Vivekachūḍāmaṇi)

If unavailable, return: "Not specified". Do not fabricate.

==================================================================
PART 2 — VERBATIM QUOTE EXTRACTION
==================================================================
STRICT REQUIREMENTS:
1. Quotes MUST remain exactly verbatim — the speaker's exact words.
2. Do not paraphrase, rewrite, summarize, or grammatically correct.
3. Select quotes that are: philosophically deep, spiritually insightful, emotionally powerful, self-contained.
4. Avoid: filler speech, repetitive statements, transitional phrases, incomplete thoughts.
5. Never invent or reconstruct missing content.

==================================================================
PART 3 — CONTENT ASSET GENERATION
==================================================================
A. BEST QUOTE — single most powerful verbatim quote.
B. YOUTUBE TITLE — Format: "Discourse | <Topic> | <Insight>" — concise, YouTube-friendly.
C. MAIN TAKEAWAY — 1–2 sentence essence of the discourse.
D. REEL CAPTION — from best quote, emotionally engaging, max 2 lines.
E. HASHTAGS — 8–12 relevant hashtags: #Vedanta #Advaita #SelfKnowledge #Spirituality #Mindfulness etc.

==================================================================
PART 4 — THEMATIC TAGGING
==================================================================
Assign each quote one theme from:
Self / Ātman | Brahman / Non-duality | Ego | Karma | Devotion | Detachment | Mind | Knowledge

==================================================================
OUTPUT — STRICT JSON ONLY, no markdown fences, no explanation
==================================================================
{
  "speaker": "name or Not specified",
  "topic": "topic or Not specified",
  "scripture": "scripture or Not specified",
  "quotes": [
    {"text": "exact verbatim quote", "theme": "Self / Ātman"}
  ],
  "best_quote": "most powerful quote",
  "youtube_title": "Discourse | Topic | Insight",
  "main_takeaway": "1-2 sentence essence",
  "reel_caption": "short emotionally engaging caption",
  "hashtags": ["#vedanta", "#advaita"]
}"""


def call_extractor(transcript: str, anthropic_key: str) -> dict:
    import urllib.request
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "system": EXTRACTOR_PROMPT,
        "messages": [{"role": "user", "content": f"Discourse transcript:\n\n{transcript}"}]
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
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    raw = data["content"][0]["text"].strip()

    # Strategy 1: strip markdown fences
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    # Strategy 2: if still not valid JSON, extract the { ... } block
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Find the first { and last } and extract that substring
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start != -1 and end > start:
            candidate = raw[start:end]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        # Strategy 3: fix common issues — unescaped quotes inside strings,
        # trailing commas before closing brackets
        cleaned = re.sub(r',\s*}', '}', raw)
        cleaned = re.sub(r',\s*]', ']', cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Last resort: extract again from cleaned
            start = cleaned.find("{")
            end   = cleaned.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(cleaned[start:end])
            raise


THEME_COLORS = {
    "Self / Ātman":          "#c9a96e",
    "Brahman / Non-duality": "#8fa8c8",
    "Ego":                   "#c87a6e",
    "Karma":                 "#a8c88f",
    "Devotion":              "#c88fa8",
    "Detachment":            "#8fc8c8",
    "Mind":                  "#c8c88f",
    "Knowledge":             "#b8a88a",
}


def render_results(result: dict):
    # ── Discourse header ──────────────────────────────────────────────────────
    st.markdown("""
    <div style='background:#111;border:1px solid #2a2a2a;border-top:4px solid #c9a96e;
    border-radius:12px;padding:1.2rem 1.8rem;margin-bottom:1.5rem;'>
    <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
    letter-spacing:1px;font-weight:600;margin-bottom:1rem;'>✦ Discourse Details</div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**🎙️ Speaker**")
        st.markdown(f"<span style='font-size:0.82rem;font-weight:700;'>{result.get('speaker','—')}</span>", unsafe_allow_html=True)
    with c2:
        st.markdown("**📖 Topic**")
        st.markdown(f"<span style='font-size:0.82rem;font-weight:700;'>{result.get('topic','—')}</span>", unsafe_allow_html=True)
    with c3:
        st.markdown("**📚 Scripture**")
        st.markdown(f"<span style='font-size:0.82rem;font-weight:700;color:#c9a96e;'>{result.get('scripture','—')}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Best quote ────────────────────────────────────────────────────────────
    best = result.get("best_quote", "")
    if best:
        st.markdown(f"""
        <div style='background:#0d0d0d;border:1px solid #2a2a2a;border-left:4px solid #c9a96e;
        border-radius:12px;padding:1.6rem 2rem;margin-bottom:1.5rem;text-align:center;'>
            <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
            letter-spacing:1px;margin-bottom:0.8rem;'>💎 Best Quote</div>
            <div style='font-family:Cormorant Garamond,serif;font-style:italic;
            font-size:1.15rem;color:#e8e0d4;line-height:1.9;'>"{best}"</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Content assets ────────────────────────────────────────────────────────
    st.markdown("<div class='step-label'>Content Assets</div>", unsafe_allow_html=True)
    ca1, ca2 = st.columns(2)
    with ca1:
        yt = result.get("youtube_title", "")
        st.markdown(f"""
        <div style='background:#111;border:1px solid #2a2a2a;border-radius:10px;
        padding:1rem 1.2rem;margin-bottom:1rem;'>
            <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
            letter-spacing:0.8px;margin-bottom:0.5rem;'>▶ YouTube Title</div>
            <div style='font-size:0.88rem;color:#e8e0d4;font-weight:600;line-height:1.6;'>{yt}</div>
        </div>""", unsafe_allow_html=True)
        reel = result.get("reel_caption", "")
        st.markdown(f"""
        <div style='background:#111;border:1px solid #2a2a2a;border-radius:10px;
        padding:1rem 1.2rem;'>
            <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
            letter-spacing:0.8px;margin-bottom:0.5rem;'>📱 Reel / Short Caption</div>
            <div style='font-size:0.88rem;color:#e8e0d4;font-style:italic;line-height:1.6;'>{reel}</div>
        </div>""", unsafe_allow_html=True)
    with ca2:
        takeaway = result.get("main_takeaway", "")
        st.markdown(f"""
        <div style='background:#111;border:1px solid #2a2a2a;border-radius:10px;
        padding:1rem 1.2rem;margin-bottom:1rem;'>
            <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
            letter-spacing:0.8px;margin-bottom:0.5rem;'>✨ Main Takeaway</div>
            <div style='font-size:0.88rem;color:#c8bfb0;line-height:1.7;'>{takeaway}</div>
        </div>""", unsafe_allow_html=True)
        hashtags = result.get("hashtags", [])
        tags_html = " ".join(
            f"<span style='background:#161616;border:1px solid #2a2a2a;border-radius:20px;"
            f"padding:2px 10px;font-size:0.75rem;color:#c9a96e;margin:2px;display:inline-block;'>{h}</span>"
            for h in hashtags
        )
        st.markdown(f"""
        <div style='background:#111;border:1px solid #2a2a2a;border-radius:10px;
        padding:1rem 1.2rem;'>
            <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
            letter-spacing:0.8px;margin-bottom:0.6rem;'># Hashtags</div>
            <div>{tags_html}</div>
        </div>""", unsafe_allow_html=True)

    # ── All quotes ────────────────────────────────────────────────────────────
    quotes = result.get("quotes", [])
    if quotes:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("<div class='step-label'>All Extracted Quotes</div>", unsafe_allow_html=True)
        for q in quotes:
            theme = q.get("theme", "")
            color = THEME_COLORS.get(theme, "#888")
            text  = q.get("text", "")
            st.markdown(f"""
            <div style='background:#111;border:1px solid #1e1e1e;border-left:3px solid {color};
            border-radius:10px;padding:1rem 1.4rem;margin-bottom:0.8rem;'>
                <div style='font-size:0.7rem;color:{color};text-transform:uppercase;
                letter-spacing:0.8px;margin-bottom:0.5rem;'>{theme}</div>
                <div style='font-family:Cormorant Garamond,serif;font-style:italic;
                font-size:0.98rem;color:#d4c9b8;line-height:1.8;'>"{text}"</div>
            </div>""", unsafe_allow_html=True)

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div class='step-label'>Export</div>", unsafe_allow_html=True)
    lines = [
        "══════════════════════════════════════════════════",
        "                  QUOTE STREAM",
        "══════════════════════════════════════════════════",
        "",
        f"  SPEAKER:    {result.get('speaker','')}",
        f"  TOPIC:      {result.get('topic','')}",
        f"  SCRIPTURE:  {result.get('scripture','')}",
        "",
        "──────────────────────────────────────────────────",
        "  ★ BEST QUOTE",
        "──────────────────────────────────────────────────",
        f'  "{result.get("best_quote","")}"',
        "",
        "──────────────────────────────────────────────────",
        "  ▶ YOUTUBE TITLE",
        "──────────────────────────────────────────────────",
        f"  {result.get('youtube_title','')}",
        "",
        "──────────────────────────────────────────────────",
        "  ✨ MAIN TAKEAWAY",
        "──────────────────────────────────────────────────",
        f"  {result.get('main_takeaway','')}",
        "",
        "──────────────────────────────────────────────────",
        "  📱 REEL CAPTION",
        "──────────────────────────────────────────────────",
        f"  {result.get('reel_caption','')}",
        "",
        "──────────────────────────────────────────────────",
        "  # HASHTAGS",
        "──────────────────────────────────────────────────",
        f"  {' '.join(result.get('hashtags',[]))}",
        "",
        "══════════════════════════════════════════════════",
        "  ALL EXTRACTED QUOTES",
        "══════════════════════════════════════════════════",
    ]
    for i, q in enumerate(result.get("quotes", []), 1):
        theme = q.get("theme", "").upper()
        text  = q.get("text", "")
        lines += [
            "",
            f"  {i}.  [ {theme} ]",
            f'  "{text}"',
        ]
    export_text = "\n".join(lines)


    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        st.download_button("📄 TXT", export_text,
                           file_name="wisdom_extractor.txt", mime="text/plain")
    with dc2:
        try:
            # Build rich markdown for PDF so bold/headings render properly
            md_lines = [
                f"## Best Quote",
                f'*"{result.get("best_quote","")}"*',
                "",
                f"## YouTube Title",
                result.get("youtube_title",""),
                "",
                f"## Main Takeaway",
                result.get("main_takeaway",""),
                "",
                f"## Reel Caption",
                result.get("reel_caption",""),
                "",
                f"## Hashtags",
                " ".join(result.get("hashtags",[])),
                "",
                "---",
                "## All Extracted Quotes",
            ]
            for i, q in enumerate(result.get("quotes",[]), 1):
                md_lines += [
                    "",
                    f"### {i}. {q.get('theme','')}",
                    f'*"{q.get("text","")}"*',
                ]
            pdf_content = "\n".join(md_lines)
            pdf = make_pdf("Wisdom Extractor", pdf_content,
                           speaker=result.get("speaker",""),
                           topic=result.get("topic",""),
                           scripture=result.get("scripture",""))
            st.download_button("📕 PDF", pdf,
                               file_name="wisdom_extractor.pdf", mime="application/pdf")
        except Exception as e:
            st.caption(f"PDF: {e}")
    with dc3:
        try:
            docx = make_docx("Wisdom Extractor", export_text,
                             speaker=result.get("speaker",""),
                             topic=result.get("topic",""),
                             scripture=result.get("scripture",""))
            st.download_button("📘 DOCX", docx,
                               file_name="wisdom_extractor.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        except Exception as e:
            st.caption(f"DOCX: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════════════════════════════════════

anthropic_key = st.session_state.get("anthropic_key", "")
openai_key    = st.session_state.get("openai_key", "")

if not anthropic_key:
    st.warning("⚠️ Please enter your Anthropic API key on the Home page.")
    st.stop()

# ── Step 1 — Input source ─────────────────────────────────────────────────────
st.markdown("<div class='step-label'>Step 1 — Choose Input</div>", unsafe_allow_html=True)
tab_audio, tab_text, tab_file = st.tabs(["🎙️ Audio File", "✍️ Paste Transcript", "📄 Upload .txt"])

transcript_text = st.session_state.get("qs_transcript", "")

with tab_audio:
    st.markdown(
        "<div style='font-size:0.82rem;color:#888;margin-bottom:0.8rem;'>"
        "Upload an MP3, M4A, or WAV file. The audio will be transcribed using Whisper "
        "and the exact words used for quote extraction.</div>",
        unsafe_allow_html=True
    )
    if not openai_key:
        st.warning("⚠️ OpenAI key required for audio transcription. Please add it on the Home page.")
    else:
        audio_file = st.file_uploader(
            "Upload audio file",
            type=["mp3", "m4a", "wav", "ogg"],
            key="qs_audio"
        )
        a1, a2 = st.columns(2)
        with a1:
            speaker_audio = st.text_input("🎙️ Speaker name (optional)", key="qs_spk_audio",
                                          placeholder="e.g. Swami Aparājitānandajī")
        with a2:
            scripture_audio = st.text_input("📚 Scripture (optional)", key="qs_scr_audio",
                                            placeholder="e.g. Bhagavad Gītā")

        if audio_file and st.button("🎙️ Transcribe Audio", key="qs_transcribe"):
            if not openai_key:
                st.error("OpenAI key needed for transcription.")
            else:
                suffix = Path(audio_file.name).suffix
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(audio_file.read())
                    tmp_path = tmp.name
                try:
                    with st.spinner("Transcribing audio with Whisper…"):
                        progress = st.progress(0)
                        status   = st.empty()
                        chunks   = split_audio_ffmpeg(tmp_path)
                        raw_text = transcribe_chunks(
                            chunks, openai_key, progress, status,
                            speaker=speaker_audio,
                            scripture=scripture_audio
                        )
                        st.session_state["qs_transcript"] = raw_text
                        transcript_text = raw_text
                        progress.progress(100)
                        status.success("✅ Transcription complete!")
                finally:
                    os.unlink(tmp_path)
                    for c in chunks:
                        try: os.unlink(c)
                        except: pass

        if st.session_state.get("qs_transcript"):
            with st.expander("📜 View transcript", expanded=False):
                st.text_area("Transcript", st.session_state["qs_transcript"],
                             height=200, key="qs_tx_preview", disabled=True)

with tab_text:
    pasted = st.text_area(
        "Paste the discourse transcript here",
        height=260,
        placeholder="Paste the full transcript of the discourse…",
        key="qs_paste"
    )
    if pasted:
        transcript_text = pasted

with tab_file:
    uploaded = st.file_uploader("Upload a .txt transcript file", type=["txt"], key="qs_upload")
    if uploaded:
        transcript_text = uploaded.read().decode("utf-8", errors="ignore")
        st.success(f"✅ Loaded: {uploaded.name} ({len(transcript_text):,} characters)")

# ── Step 2 — Options ─────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<div class='step-label'>Step 2 — Speaker, Scripture & Focus Keywords (optional)</div>", unsafe_allow_html=True)

o1, o2 = st.columns(2)
with o1:
    speaker_hint  = st.text_input("🎙️ Speaker name", key="qs_spk",
                                   placeholder="e.g. Swami Aparājitānandajī")
with o2:
    scripture_hint = st.text_input("📚 Scripture / Text", key="qs_scr",
                                    placeholder="e.g. Bhagavad Gītā Ch.15")

st.markdown(
    "<div style='font-size:0.82rem;color:#888;margin:0.4rem 0 0.3rem;'>"
    "🔍 <b style='color:#b8a88a;'>Focus Keywords</b> — Enter specific themes, concepts, or "
    "Sanskrit terms you want the AI to prioritize when extracting quotes. "
    "Leave blank to extract the most impactful quotes overall.</div>",
    unsafe_allow_html=True
)
keyword_hints = st.text_input(
    "Focus keywords (optional)",
    key="qs_keywords",
    placeholder="e.g. surrender, ego, Ātman, devotion, karma, instrument of God",
    label_visibility="collapsed"
)

# ── Step 3 — Extract ──────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
if st.button("💎 Extract Wisdom", key="qs_process", use_container_width=True):
    if not transcript_text or not transcript_text.strip():
        st.error("Please provide a transcript — via audio transcription, paste, or file upload.")
    else:
        full_input = transcript_text
        hints = []
        if speaker_hint:   hints.append(f"Speaker: {speaker_hint}")
        if scripture_hint: hints.append(f"Scripture: {scripture_hint}")
        if keyword_hints:  hints.append(
            f"PRIORITY FOCUS: When selecting quotes, prioritize teachings related to these "
            f"themes/keywords: {keyword_hints}. Still extract verbatim — do not paraphrase."
        )
        if hints:
            full_input = "\n".join(hints) + "\n\n" + transcript_text
        with st.spinner("Extracting wisdom from the discourse…"):
            try:
                result = call_extractor(full_input, anthropic_key)
                st.session_state["qs_result"] = result
            except json.JSONDecodeError as e:
                st.error(f"Could not parse AI response as JSON: {e}")
                with st.expander("🔍 Raw AI response (for debugging)"):
                    st.text(str(e))
            except Exception as e:
                st.error(f"Extraction failed: {e}")

# ── Results ───────────────────────────────────────────────────────────────────
if "qs_result" in st.session_state:
    st.markdown("<hr style='border-color:#1e1e1e;margin:1.5rem 0;'/>", unsafe_allow_html=True)
    render_results(st.session_state["qs_result"])
    if st.button("🔄 Clear and start over", key="qs_clear"):
        for k in ["qs_result", "qs_transcript"]:
            st.session_state.pop(k, None)
        st.rerun()
