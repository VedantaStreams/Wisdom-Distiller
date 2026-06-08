
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
# ── Require login ─────────────────────────────────────────────────────────────
def _check_login():
    is_logged_in = False
    try:
        user = st.experimental_user
        is_logged_in = user is not None and bool(getattr(user, "email", None))
    except Exception:
        try:
            user = st.user
            is_logged_in = user is not None and bool(getattr(user, "email", None))
        except Exception:
            pass
    if not is_logged_in:
        st.warning("Please sign in via the Home page to use this feature.")
        if st.button("Go to Home page"):
            st.switch_page("app.py")
        st.stop()
_check_login()



with st.sidebar:
    try:
        st.page_link("app.py", label="🏠 Home")
    except Exception:
        if st.button("🏠 Home", key="home_btn_" + __file__[-20:]):
            st.switch_page("app.py")
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
EXTRACTOR_PROMPT = """You are a senior scholar and devoted student of Vedānta, deeply familiar with
Advaita Vedānta, the Upaniṣads, Bhagavad Gītā, and the Chinmaya Mission tradition of teaching.

Your task is to read the discourse transcript with full comprehension — understanding its
philosophical arc, key arguments, examples used, and spiritual insights — and then surface
the most luminous, self-contained, verbatim quotes the teacher actually spoke.

CRITICAL SANSKRIT RULE: Any Sanskrit verse, shloka, or mantra MUST be displayed in
Devanāgarī script ONLY (e.g. श्रेयान्स्वधर्मो विगुणः, ॐ तत् सत्).
Do NOT transliterate Sanskrit verses into Roman/English script.
After the Devanāgarī, you may provide the meaning in English.
For Swamiji names, use proper transliteration (e.g. Swāmī Aparājitānandajī, Swāmī Śaraṇānandajī).

==================================================================
STEP 1 — DEEP COMPREHENSION (internal reasoning, not in output)
==================================================================
Before selecting any quotes, read the entire transcript and internally note:
- The central philosophical teaching and its progression
- Key arguments, analogies, and examples used
- Moments of highest spiritual insight or emotional resonance
- The teacher's most precise, memorable, and self-contained statements
- How individual statements connect to the overall teaching arc

This comprehension step ensures quotes are selected for their TRUE depth and contextual
significance — not merely because they sound profound in isolation.

==================================================================
STEP 2 — METADATA
==================================================================
Extract:
1. Speaker Name (proper transliteration)
2. Topic / Main Theme
3. Referenced Scripture (e.g. Bhagavad Gītā, Upaniṣads, Vivekachūḍāmaṇi)
If unavailable: "Not specified". Never fabricate.

==================================================================
STEP 3 — NOTABLE QUOTE SELECTION
==================================================================
Now select the most notable verbatim quotes — exactly as the teacher spoke them.

SELECTION CRITERIA (apply all):
✦ Philosophically precise — captures a teaching with clarity and completeness
✦ Spiritually resonant — would move or awaken a sincere seeker
✦ Memorable and self-contained — meaningful even without surrounding context
✦ Authentic to the teacher's voice — preserves their natural phrasing and rhythm
✦ Non-redundant — each quote offers a distinct insight; avoid repetition of themes
✦ Represents the arc — collectively the quotes should reflect the full journey of the talk

VERBATIM RULES — WITH MINOR GRAMMATICAL POLISH:
1. Preserve the teacher's exact words, meaning, and phrasing faithfully
2. You MAY make minimal grammatical corrections only — such as:
   - Fixing subject-verb agreement ("he have" → "he has")
   - Adding a missing article ("a", "an", "the") where clearly implied
   - Correcting obvious spoken errors that would confuse a reader
3. Do NOT change vocabulary, rephrase sentences, or alter the teacher's natural voice
4. Do NOT combine sentences from different parts of the talk
5. Do NOT complete unfinished thoughts or add ideas not spoken
6. Do NOT over-correct — preserve the teacher's spoken style and rhythm
7. Prefer complete, self-contained statements over fragments
8. If a quote uses an analogy or example, include enough context to make it whole

AVOID:
- Transitional phrases ("so," "now," "as I said")
- Administrative speech ("let us look at," "we will now see")
- Incomplete or fragmented sentences
- Filler or repetitive content

TARGET: 8–12 quotes that together paint a vivid picture of the entire discourse.

==================================================================
STEP 4 — THEMATIC TAGGING
==================================================================
Assign each quote ONE theme:
Self / Ātman | Brahman / Non-duality | Ego | Karma | Devotion | Detachment | Mind | Knowledge

==================================================================
STEP 5 — CONTENT ASSETS
==================================================================
A. BEST QUOTE — the single most powerful, complete, and resonant verbatim quote
B. YOUTUBE TITLE — "Discourse | <Topic> | <Core Insight>" — concise, impactful
C. MAIN TAKEAWAY — 1–2 sentences capturing the essence of the entire discourse
D. REEL CAPTION — emotionally engaging, derived from best quote, max 2 lines
E. HASHTAGS — 8–12: #Vedanta #Advaita #SelfKnowledge #Spirituality #Mindfulness
   #Devotion + discourse-specific concepts

==================================================================
OUTPUT — STRICT JSON ONLY, no markdown fences, no preamble, no explanation
==================================================================
{
  "speaker": "name or Not specified",
  "topic": "topic or Not specified",
  "scripture": "scripture or Not specified",
  "quotes": [
    {"text": "exact verbatim quote as spoken", "theme": "Devotion"}
  ],
  "best_quote": "single most powerful verbatim quote",
  "youtube_title": "Discourse | Topic | Core Insight",
  "main_takeaway": "1-2 sentence essence of the discourse",
  "reel_caption": "short emotionally engaging caption max 2 lines",
  "hashtags": ["#vedanta", "#advaita", "#selfknowledge"]
}"""


def call_extractor(transcript: str, anthropic_key: str) -> dict:
    import anthropic as _anthropic
    client = _anthropic.Anthropic(api_key=anthropic_key)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=EXTRACTOR_PROMPT,
        messages=[{"role": "user", "content": f"Discourse transcript:\n\n{transcript}"}]
    )
    raw = msg.content[0].text.strip()

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
