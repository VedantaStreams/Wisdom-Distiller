import streamlit as st
import sys
import json
import re
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
from utils.helpers import make_pdf, make_docx, LANGUAGES

st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── Home button in sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.page_link("app.py", label="🏠 Home")
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>💎 Wisdom <span class="accent">Extractor</span></h1>
    <p class="subtitle">Verbatim quotes · YouTube titles · Reels · Hashtags</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="about-box">
    Paste or upload a discourse transcript. The AI will extract the most profound
    verbatim quotes, generate a YouTube title, reel caption, main takeaway, and
    hashtags — all structured and ready to use.
</div>
""", unsafe_allow_html=True)

# ── System prompt (exact spec) ────────────────────────────────────────────────
EXTRACTOR_PROMPT = """You are an expert curator of Vedantic discourses with specialization in:
- Verbatim wisdom extraction
- Vedantic thematic understanding
- Structured metadata generation
- High-quality content asset generation for YouTube, reels, and social media

Your objective is to extract the most profound teachings while preserving the exact spoken words of the teacher.

==================================================================
PART 1 — METADATA EXTRACTION
==================================================================
From the discourse, identify and extract:
1. Speaker Name
2. Topic / Main Theme
3. Referenced Scriptural Text (e.g. Bhagavad Gītā, Upaniṣads, Vivekachūḍāmaṇi, Bhaja Govindam, Soundarya Lahari)

RULES:
- Extract only information explicitly mentioned or strongly inferable.
- Do not hallucinate or fabricate metadata.
- If information is unavailable, return: "Not specified"
- For all Swamiji names, use proper English transliteration (e.g. Swami Aparājitānanda ji)
- For Sanskrit verses, always include original Devanāgarī script alongside transliteration.

==================================================================
PART 2 — VERBATIM QUOTE EXTRACTION
==================================================================
Extract the most impactful and meaningful quotes from the discourse.

STRICT REQUIREMENTS:
1. Quotes MUST remain exactly verbatim.
2. Do not paraphrase, rewrite, summarize, or grammatically correct.
3. Preserve the speaker's natural tone and wording.
4. Select quotes that are: philosophically deep, spiritually insightful, emotionally powerful, memorable and self-contained.
5. Avoid: repetitive statements, filler speech, transitional phrases, incomplete thoughts.
6. Never invent or reconstruct missing content.

==================================================================
PART 3 — CONTENT ASSET GENERATION
==================================================================
A. BEST QUOTE — the single most powerful quote.
B. YOUTUBE TITLE — Format: "Discourse | <Topic> | <Insight>" — concise, impactful, YouTube-friendly.
C. MAIN TAKEAWAY — 1–2 sentence essence of the discourse.
D. REEL / SHORT CAPTION — derived from the best quote, emotionally engaging, max 1–2 lines.
E. HASHTAGS — 8–12 relevant hashtags combining: Vedanta, Spirituality, SelfKnowledge, Advaita, Mindfulness, Devotion, and discourse-specific concepts.

==================================================================
PART 4 — THEMATIC TAGGING
==================================================================
Assign a thematic category to every quote from:
Self / Ātman | Brahman / Non-duality | Ego | Karma | Devotion | Detachment | Mind | Knowledge

==================================================================
OUTPUT FORMAT — STRICT JSON ONLY
==================================================================
Return ONLY valid JSON, no explanation, no markdown fences:

{
  "speaker": "<name or Not specified>",
  "topic": "<topic or Not specified>",
  "scripture": "<scripture or Not specified>",
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
    """Call Claude API with the extraction prompt."""
    import urllib.request
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "system": EXTRACTOR_PROMPT,
        "messages": [{"role": "user", "content": f"Here is the discourse transcript:\n\n{transcript}"}]
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
    # Strip markdown fences if present
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def render_results(result: dict):
    """Render the extracted wisdom in a beautiful layout."""

    # ── Metadata header ───────────────────────────────────────────────────────
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
        </div>
        """, unsafe_allow_html=True)

        reel = result.get("reel_caption", "")
        st.markdown(f"""
        <div style='background:#111;border:1px solid #2a2a2a;border-radius:10px;
        padding:1rem 1.2rem;'>
            <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
            letter-spacing:0.8px;margin-bottom:0.5rem;'>📱 Reel / Short Caption</div>
            <div style='font-size:0.88rem;color:#e8e0d4;font-style:italic;line-height:1.6;'>{reel}</div>
        </div>
        """, unsafe_allow_html=True)

    with ca2:
        takeaway = result.get("main_takeaway", "")
        st.markdown(f"""
        <div style='background:#111;border:1px solid #2a2a2a;border-radius:10px;
        padding:1rem 1.2rem;margin-bottom:1rem;'>
            <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
            letter-spacing:0.8px;margin-bottom:0.5rem;'>✨ Main Takeaway</div>
            <div style='font-size:0.88rem;color:#c8bfb0;line-height:1.7;'>{takeaway}</div>
        </div>
        """, unsafe_allow_html=True)

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
        </div>
        """, unsafe_allow_html=True)

    # ── All quotes with themes ─────────────────────────────────────────────────
    quotes = result.get("quotes", [])
    if quotes:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("<div class='step-label'>All Extracted Quotes</div>", unsafe_allow_html=True)

        THEME_COLORS = {
            "Self / Ātman":        "#c9a96e",
            "Brahman / Non-duality": "#8fa8c8",
            "Ego":                 "#c87a6e",
            "Karma":               "#a8c88f",
            "Devotion":            "#c88fa8",
            "Detachment":          "#8fc8c8",
            "Mind":                "#c8c88f",
            "Knowledge":           "#b8a88a",
        }

        for i, q in enumerate(quotes, 1):
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
            </div>
            """, unsafe_allow_html=True)

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div class='step-label'>Export</div>", unsafe_allow_html=True)

    # Build plain-text export content
    export_lines = [
        f"SPEAKER: {result.get('speaker','')}",
        f"TOPIC: {result.get('topic','')}",
        f"SCRIPTURE: {result.get('scripture','')}",
        "",
        f"BEST QUOTE:\n\"{result.get('best_quote','')}\"",
        "",
        f"YOUTUBE TITLE:\n{result.get('youtube_title','')}",
        "",
        f"MAIN TAKEAWAY:\n{result.get('main_takeaway','')}",
        "",
        f"REEL CAPTION:\n{result.get('reel_caption','')}",
        "",
        f"HASHTAGS:\n{' '.join(result.get('hashtags',[]))}",
        "",
        "═" * 50,
        "ALL QUOTES",
        "═" * 50,
    ]
    for q in result.get("quotes", []):
        export_lines.append(f"\n[{q.get('theme','')}]")
        export_lines.append(f'"{q.get("text","")}"')

    export_text = "\n".join(export_lines)

    dcol1, dcol2, dcol3 = st.columns(3)
    with dcol1:
        st.download_button("📄 Download TXT", export_text,
                           file_name="wisdom_quotes.txt", mime="text/plain")
    with dcol2:
        try:
            pdf_bytes = make_pdf("Wisdom Extractor", export_text,
                                 speaker=result.get("speaker",""),
                                 topic=result.get("topic",""),
                                 scripture=result.get("scripture",""))
            st.download_button("📕 Download PDF", pdf_bytes,
                               file_name="wisdom_quotes.pdf", mime="application/pdf")
        except Exception as e:
            st.caption(f"PDF error: {e}")
    with dcol3:
        try:
            docx_bytes = make_docx("Wisdom Extractor", export_text,
                                   speaker=result.get("speaker",""),
                                   topic=result.get("topic",""),
                                   scripture=result.get("scripture",""))
            st.download_button("📘 Download DOCX", docx_bytes,
                               file_name="wisdom_quotes.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        except Exception as e:
            st.caption(f"DOCX error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════════════════════════════════════

anthropic_key = st.session_state.get("anthropic_key", "")
if not anthropic_key:
    st.warning("⚠️ Please enter your Anthropic API key on the Home page to use this feature.")
    st.stop()

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("<div class='step-label'>Step 1 — Provide Transcript</div>", unsafe_allow_html=True)

input_tab1, input_tab2 = st.tabs(["✍️ Paste Text", "📄 Upload .txt File"])

transcript_text = ""

with input_tab1:
    transcript_text = st.text_area(
        "Paste the discourse transcript here",
        height=280,
        placeholder="Paste the full transcript of the discourse here...",
        key="we_paste"
    )

with input_tab2:
    uploaded = st.file_uploader("Upload a .txt transcript file", type=["txt"], key="we_upload")
    if uploaded:
        transcript_text = uploaded.read().decode("utf-8", errors="ignore")
        st.success(f"✅ Loaded: {uploaded.name} ({len(transcript_text):,} characters)")

# ── Options ───────────────────────────────────────────────────────────────────
st.markdown("<div class='step-label'>Step 2 — Options</div>", unsafe_allow_html=True)

oc1, oc2 = st.columns(2)
with oc1:
    speaker_hint = st.text_input("🎙️ Speaker name (optional)", placeholder="e.g. Swami Aparājitānandajī")
with oc2:
    scripture_hint = st.text_input("📚 Scripture (optional)", placeholder="e.g. Bhagavad Gītā")

# ── Process ───────────────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
if st.button("💎 Extract Wisdom", key="we_process"):
    if not transcript_text.strip():
        st.error("Please paste or upload a transcript first.")
    else:
        # Prepend hints to transcript if provided
        full_input = transcript_text
        if speaker_hint or scripture_hint:
            hints = []
            if speaker_hint:  hints.append(f"Speaker: {speaker_hint}")
            if scripture_hint: hints.append(f"Scripture: {scripture_hint}")
            full_input = "\n".join(hints) + "\n\n" + transcript_text

        with st.spinner("Extracting wisdom from the discourse…"):
            try:
                result = call_extractor(full_input, anthropic_key)
                st.session_state["we_result"] = result
            except json.JSONDecodeError as e:
                st.error(f"Could not parse response as JSON: {e}")
            except Exception as e:
                st.error(f"Extraction failed: {e}")

# ── Show results if available ─────────────────────────────────────────────────
if "we_result" in st.session_state:
    st.markdown("<hr style='border-color:#1e1e1e;margin:1.5rem 0;'/>", unsafe_allow_html=True)
    render_results(st.session_state["we_result"])

    if st.button("🔄 Clear and start over", key="we_clear"):
        del st.session_state["we_result"]
        st.rerun()
