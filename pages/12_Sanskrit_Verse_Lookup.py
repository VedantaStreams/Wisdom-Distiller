import streamlit as st
import sys
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="Sanskrit Verse Lookup · Wisdom Distiller",
    page_icon="🕉️",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils.styles import SHARED_CSS
from utils.helpers import make_pdf, make_docx

st.markdown(SHARED_CSS, unsafe_allow_html=True)

with st.sidebar:
    try:
        st.page_link("app.py", label="🏠 Home")
    except Exception:
        pass
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>",
                unsafe_allow_html=True)

anthropic_key = st.session_state.get("anthropic_key", "")
if not anthropic_key:
    try: anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
    except: pass

st.markdown("""
<div class="hero">
    <h1>🕉️ Sanskrit Verse <span class="accent">Lookup</span></h1>
    <p class="subtitle">Identify · Understand · Explore</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="about-box">
    Enter any Sanskrit verse, partial phrase, or transliteration you heard in a discourse.
    The AI will identify its source, display the full verse in
    <b style='color:#c9a96e;'>Devanāgarī script</b>, provide word-by-word meaning,
    overall translation, and context within the scripture.
</div>
""", unsafe_allow_html=True)

LOOKUP_PROMPT = """You are a master Vedantic scholar with complete knowledge of all major
Sanskrit scriptures — Upaniṣads, Bhagavad Gītā, Brahma Sūtras, Vivekachūḍāmaṇi,
Prakaraṇa Granthas, Purāṇas, Rāmāyaṇa, Mahābhārata, and the stotra literature.

A seeker will give you a Sanskrit verse, partial phrase, or transliteration.
Your task is to identify it and provide complete scholarly information.

CRITICAL: All Sanskrit must appear in Devanāgarī script. Never use Roman transliteration
for verses — only for word-by-word breakdown where helpful.

If you cannot identify the verse with confidence, say so honestly — never fabricate.

Respond in STRICT JSON ONLY (no markdown fences):

{
  "found": true or false,
  "confidence": "high / medium / low",
  "verse_devanagari": "Complete verse in Devanāgarī",
  "verse_transliteration": "Roman transliteration with diacritics",
  "source": "Scripture name",
  "reference": "Chapter.Verse or equivalent reference",
  "word_meanings": [
    {"word": "Sanskrit word", "meaning": "English meaning"}
  ],
  "overall_meaning": "Complete meaning of the verse in clear English",
  "context": "Context within the scripture — what comes before/after and why this verse matters",
  "significance": "Why this verse is significant in Vedantic teaching",
  "commonly_referenced_in": "Other scriptures or teachings where this verse is cited",
  "note": "Any additional note — or empty string if not needed"
}"""


def lookup_verse(query: str, anthropic_key: str) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=anthropic_key)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        system=LOOKUP_PROMPT,
        messages=[{"role": "user", "content": f"Please identify this verse or phrase:\n\n{query}"}]
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    start = raw.find('{')
    end   = raw.rfind('}') + 1
    if start != -1 and end > start:
        raw = raw[start:end]
    return json.loads(raw)


# ── UI ────────────────────────────────────────────────────────────────────────
if not anthropic_key:
    st.warning("⚠️ Please enter your Anthropic API key on the Home page.")
    st.stop()

st.markdown("<div class='step-label'>Enter a Verse or Phrase</div>", unsafe_allow_html=True)
st.markdown(
    "<div style='font-size:0.82rem;color:#666;margin-bottom:0.5rem;'>"
    "You can enter: Devanāgarī script · Roman transliteration · "
    "Partial phrase · English description of the verse</div>",
    unsafe_allow_html=True
)

query = st.text_area(
    "Verse input",
    height=120,
    key="svl_query",
    placeholder=(
        "Examples:\n"
        "• श्रेयान्स्वधर्मो विगुणः परधर्मात्\n"
        "• Sreyan svadharmo vigunah paradharmat\n"
        "• The verse about the inverted tree with roots above\n"
        "• Aham Brahmasmi"
    ),
    label_visibility="collapsed"
)

st.markdown("<br/>", unsafe_allow_html=True)
if st.button("🕉️ Look Up Verse", key="svl_process", use_container_width=True):
    if not query.strip():
        st.error("Please enter a verse or phrase to look up.")
    else:
        with st.spinner("Searching the scriptures…"):
            try:
                result = lookup_verse(query, anthropic_key)
                st.session_state["svl_result"] = result
                st.session_state["svl_query_text"] = query
            except Exception as e:
                st.error(f"Lookup failed: {e}")

if "svl_result" in st.session_state:
    r = st.session_state["svl_result"]
    st.markdown("<hr style='border-color:#1e1e1e;margin:1.5rem 0;'/>", unsafe_allow_html=True)

    if not r.get("found", False):
        st.markdown(f"""
        <div style='background:#111;border:1px solid #2a2a2a;border-left:3px solid #888;
        border-radius:10px;padding:1.2rem 1.5rem;'>
            <div style='color:#888;font-size:0.92rem;'>
            This verse could not be identified with confidence.
            {r.get('note','')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        conf_color = {"high": "#a8c88f", "medium": "#c9a96e", "low": "#c87a6e"}.get(
            r.get("confidence","").lower(), "#888"
        )

        # ── Main verse display ─────────────────────────────────────────────
        st.markdown(f"""
        <div style='background:#0d0d0d;border:1px solid #2a2a2a;border-top:4px solid #c9a96e;
        border-radius:12px;padding:1.6rem 2rem;margin-bottom:1.2rem;text-align:center;'>
            <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
            letter-spacing:1px;margin-bottom:0.3rem;'>
                {r.get('source','')} · {r.get('reference','')}
                <span style='color:{conf_color};margin-left:0.8rem;'>
                ● {r.get('confidence','').title()} confidence</span>
            </div>
            <div style='font-family:Cormorant Garamond,serif;font-size:1.6rem;
            color:#c9a96e;line-height:2;margin:0.8rem 0;'>
                {r.get('verse_devanagari','')}
            </div>
            <div style='font-size:0.82rem;color:#555;font-style:italic;'>
                {r.get('verse_transliteration','')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Word meanings ──────────────────────────────────────────────────
        words = r.get("word_meanings", [])
        if words:
            st.markdown("<div class='step-label'>Word by Word</div>", unsafe_allow_html=True)
            cols = st.columns(min(len(words), 4))
            for i, w in enumerate(words):
                with cols[i % 4]:
                    st.markdown(f"""
                    <div style='background:#111;border:1px solid #1e1e1e;border-radius:8px;
                    padding:0.6rem 0.7rem;margin-bottom:0.5rem;text-align:center;'>
                        <div style='font-size:0.9rem;color:#c9a96e;font-weight:600;'>
                        {w.get('word','')}</div>
                        <div style='font-size:0.75rem;color:#666;margin-top:0.2rem;'>
                        {w.get('meaning','')}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # ── Meaning, Context, Significance ────────────────────────────────
        for label, key, color in [
            ("Overall Meaning", "overall_meaning", "#e8e0d4"),
            ("Context in Scripture", "context", "#999"),
            ("Vedantic Significance", "significance", "#b8a88a"),
        ]:
            val = r.get(key, "")
            if val:
                st.markdown("<br/>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style='background:#111;border:1px solid #1e1e1e;border-left:3px solid #c9a96e;
                border-radius:10px;padding:1rem 1.3rem;'>
                    <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
                    letter-spacing:0.8px;margin-bottom:0.5rem;'>{label}</div>
                    <div style='font-size:0.9rem;color:{color};line-height:1.8;'>{val}</div>
                </div>
                """, unsafe_allow_html=True)

        cited = r.get("commonly_referenced_in","")
        if cited:
            st.markdown(f"""
            <br/>
            <div style='background:#111;border:1px solid #1e1e1e;border-radius:10px;
            padding:0.8rem 1.3rem;'>
                <div style='font-size:0.7rem;color:#c9a96e;text-transform:uppercase;
                letter-spacing:0.8px;margin-bottom:0.4rem;'>Also Referenced In</div>
                <div style='font-size:0.85rem;color:#666;'>{cited}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Export ─────────────────────────────────────────────────────────
        export_lines = [
            f"SANSKRIT VERSE LOOKUP",
            f"Query: {st.session_state.get('svl_query_text','')}",
            "", f"SOURCE: {r.get('source','')} {r.get('reference','')}",
            "", "VERSE (Devanāgarī):", r.get('verse_devanagari',''),
            "", "TRANSLITERATION:", r.get('verse_transliteration',''),
            "", "OVERALL MEANING:", r.get('overall_meaning',''),
            "", "CONTEXT:", r.get('context',''),
            "", "VEDANTIC SIGNIFICANCE:", r.get('significance',''),
        ]
        if words:
            export_lines += ["", "WORD BY WORD:"]
            for w in words:
                export_lines.append(f"  {w.get('word','')} — {w.get('meaning','')}")

        export_text = "\n".join(export_lines)

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("<div class='step-label'>Export</div>", unsafe_allow_html=True)
        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            st.download_button("📄 TXT", export_text,
                               file_name="verse_lookup.txt", mime="text/plain")
        with dc2:
            try:
                pdf = make_pdf("Sanskrit Verse Lookup", export_text,
                               scripture=r.get("source",""))
                st.download_button("📕 PDF", pdf, file_name="verse_lookup.pdf",
                                   mime="application/pdf")
            except Exception as e:
                st.caption(f"PDF: {e}")
        with dc3:
            try:
                docx = make_docx("Sanskrit Verse Lookup", export_text)
                st.download_button("📘 DOCX", docx, file_name="verse_lookup.docx",
                                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            except Exception as e:
                st.caption(f"DOCX: {e}")

    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("🔄 Look up another verse", key="svl_clear"):
        for k in ["svl_result","svl_query_text"]:
            st.session_state.pop(k, None)
        st.rerun()
