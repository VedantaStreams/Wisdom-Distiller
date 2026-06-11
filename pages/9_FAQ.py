import streamlit as st
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

st.set_page_config(
    page_title="FAQ · Wisdom Distiller",
    page_icon="❓",
    layout="centered",
    initial_sidebar_state="expanded",
)

from utils.styles import SHARED_CSS
st.markdown(SHARED_CSS, unsafe_allow_html=True)

with st.sidebar:
    try:
        st.page_link("app.py", label="🏠 Home")
    except Exception:
        pass
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>",
                unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>❓ Frequently Asked <span class="accent">Questions</span></h1>
    <p class="subtitle">Everything you need to know to get started</p>
</div>
""", unsafe_allow_html=True)

# ── Helper to render a FAQ section ───────────────────────────────────────────
def faq_section(title, icon, items):
    st.markdown(f"""
    <div style='margin:1.5rem 0 0.6rem;'>
        <div style='font-family:Cormorant Garamond,serif;font-size:1.3rem;
        font-weight:600;color:#c9a96e;letter-spacing:0.3px;'>
            {icon} {title}
        </div>
        <div style='height:2px;background:linear-gradient(to right,#c9a96e22,transparent);
        margin-top:0.3rem;'></div>
    </div>
    """, unsafe_allow_html=True)

    for q, a in items:
        with st.expander(q):
            st.markdown(
                f"<div style='font-size:0.92rem;color:#999;line-height:1.9;'>{a}</div>",
                unsafe_allow_html=True
            )

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — GETTING STARTED
# ══════════════════════════════════════════════════════════════════════════════
faq_section("Getting Started", "🌱", [
    (
        "What is Wisdom Distiller?",
        "Wisdom Distiller is an AI-powered app designed specifically for sincere seekers "
        "and students of Vedānta. It helps you <b style='color:#b8a88a;'>transcribe</b>, "
        "<b style='color:#b8a88a;'>summarize</b>, and "
        "<b style='color:#b8a88a;'>extract wisdom</b> from spiritual discourses — "
        "preserving Sanskrit in Devanāgarī script, supporting 7 Indian languages, "
        "and producing beautifully formatted outputs you can study, share, and archive."
    ),
    (
        "Is this app free to use?",
        "The app itself is free. However, it uses two AI services that require their own "
        "API keys — <b style='color:#b8a88a;'>Anthropic (Claude)</b> for summarization and "
        "<b style='color:#b8a88a;'>OpenAI (Whisper)</b> for audio transcription. "
        "Both offer free tiers or very low-cost usage. A typical one-hour discourse "
        "costs approximately <b style='color:#b8a88a;'>$0.05–$0.20</b> in API usage — "
        "less than a cup of tea. ☕"
    ),
    (
        "Do I need technical knowledge to use this?",
        "Not at all. If you can use WhatsApp or email, you can use this app. "
        "The only setup required is getting two API keys (step-by-step instructions below) "
        "and pasting them into the Home page sidebar. After that, everything is "
        "point-and-click — upload your audio, choose your options, and download your summary."
    ),
    (
        "What are API keys and why do I need them?",
        "An API key is like a personal password that connects the app to an AI service on "
        "your behalf. Think of it like a library card — the library (Anthropic or OpenAI) "
        "gives you a card, and you use it to borrow their services. "
        "Your keys are <b style='color:#b8a88a;'>never stored</b> by this app — "
        "they exist only in your browser session and are cleared when you close the tab."
    ),
    (
        "How do I get an Anthropic (Claude) API key?",
        "1. Go to <a href='https://console.anthropic.com' target='_blank' "
        "style='color:#c9a96e;'>console.anthropic.com</a><br/>"
        "2. Sign up for a free account<br/>"
        "3. Click <b>API Keys</b> in the left menu<br/>"
        "4. Click <b>Create Key</b>, give it a name, and copy it<br/>"
        "5. Paste it into the <b>Anthropic API Key</b> box on the Home page sidebar<br/><br/>"
        "<i>Note: New accounts receive free credits to get started.</i>"
    ),
    (
        "How do I get an OpenAI API key?",
        "1. Go to <a href='https://platform.openai.com/api-keys' target='_blank' "
        "style='color:#c9a96e;'>platform.openai.com/api-keys</a><br/>"
        "2. Sign up or log in<br/>"
        "3. Click <b>Create new secret key</b><br/>"
        "4. Copy the key immediately — you won't see it again!<br/>"
        "5. Paste it into the <b>OpenAI API Key</b> box on the Home page sidebar<br/><br/>"
        "<i>Note: OpenAI requires a small minimum deposit (~$5) to activate API access.</i>"
    ),
    (
        "Is my data safe? Is anything stored?",
        "Yes, your data is safe. This app stores <b style='color:#b8a88a;'>nothing</b> "
        "between sessions. Your API keys, audio files, and transcripts exist only in your "
        "browser's memory while the tab is open. When you close the browser, everything "
        "is cleared. No audio, transcripts, or personal information is saved to any server."
    ),
])

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — USING THE APP
# ══════════════════════════════════════════════════════════════════════════════
faq_section("Using the App", "🎙️", [
    (
        "What audio formats are supported?",
        "The app supports <b style='color:#b8a88a;'>MP3, M4A, WAV, and OGG</b> audio formats. "
        "Most phone recordings and downloaded YouTube audio will be in MP3 or M4A format, "
        "which work perfectly. Video files (MP4) are supported in the Video Summarizer page."
    ),
    (
        "How long can the audio file be?",
        "Each file can be up to <b style='color:#b8a88a;'>200MB</b>. For longer discourses, "
        "the Audio Summarizer lets you upload up to <b style='color:#b8a88a;'>5 files</b> "
        "which are processed together into one unified output. A typical 1-hour discourse "
        "in MP3 format is about 50–80MB."
    ),
    (
        "Can I upload multiple audio files?",
        "Yes — in the Audio Summarizer, you can upload up to "
        "<b style='color:#b8a88a;'>5 audio segments</b> at once. They are transcribed in "
        "order and combined into a single unified transcript and summary. This is ideal "
        "for discourses recorded across multiple sessions or days."
    ),
    (
        "Why does transcription take time?",
        "Audio transcription sends your file to OpenAI's Whisper service, which processes "
        "the speech into text. A 1-hour discourse typically takes "
        "<b style='color:#b8a88a;'>2–5 minutes</b> to transcribe, followed by another "
        "1–2 minutes for the AI to generate the summary. Please be patient — the app shows "
        "a progress bar while it works."
    ),
    (
        "What languages are supported?",
        "The app supports output in <b style='color:#b8a88a;'>7 languages</b>:<br/><br/>"
        "🇬🇧 English &nbsp;·&nbsp; 🇮🇳 Hindi &nbsp;·&nbsp; 🇮🇳 Kannada &nbsp;·&nbsp; "
        "🇮🇳 Telugu &nbsp;·&nbsp; 🇮🇳 Tamil &nbsp;·&nbsp; 🇮🇳 Marathi &nbsp;·&nbsp; "
        "🇮🇳 Gujarati<br/><br/>"
        "The transcription is always done in English first, then the summary is translated "
        "into your chosen language. Sanskrit verses always remain in Devanāgarī script "
        "regardless of the output language."
    ),
    (
        "Can I use this for non-Vedantic discourses?",
        "Yes — the app works well for any spiritual, philosophical, or educational discourse. "
        "It is optimized and tuned for Vedantic content but will produce good results for "
        "talks from other traditions, academic lectures, or any structured spoken content."
    ),
    (
        "What is the difference between the Audio Summarizer and Discourse Transcriber?",
        "<b style='color:#b8a88a;'>Audio Summarizer</b> — Produces a structured "
        "<i>summary</i> of the discourse in your chosen format (bullet points, academic "
        "digest, table, etc.). Best for quick review, note-taking, and sharing.<br/><br/>"
        "<b style='color:#b8a88a;'>Discourse Transcriber</b> — Produces the "
        "<i>complete, full transcript</i> of the discourse — every sentence, organized into "
        "sections with headings, Sanskrit glossary, and reflection. Best for deep study, "
        "archiving, and scholarly reference."
    ),
])

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — OUTPUT & DOWNLOADS
# ══════════════════════════════════════════════════════════════════════════════
faq_section("Output & Downloads", "📥", [
    (
        "What are the six output formats in the Audio Summarizer?",
        "<b style='color:#b8a88a;'>Bullet Highlights</b> — Key points as a quick bullet list<br/>"
        "<b style='color:#b8a88a;'>Main Takeaways</b> — The essential teachings in brief<br/>"
        "<b style='color:#b8a88a;'>Detailed Paragraphs</b> — Flowing prose covering all major points<br/>"
        "<b style='color:#b8a88a;'>Executive Brief</b> — A concise, structured one-page overview<br/>"
        "<b style='color:#b8a88a;'>Academic Digest</b> — Scholarly format with arguments, evidence, and notable quotes<br/>"
        "<b style='color:#b8a88a;'>Structured Table</b> — Main point · Explanation · Example · Personal Reflection columns"
    ),
    (
        "Can I download the output?",
        "Yes — every output can be downloaded in three formats:<br/><br/>"
        "📄 <b style='color:#b8a88a;'>TXT</b> — Plain text, works everywhere<br/>"
        "📕 <b style='color:#b8a88a;'>PDF</b> — Formatted document with headings and Sanskrit fonts<br/>"
        "📘 <b style='color:#b8a88a;'>DOCX</b> — Microsoft Word format, editable"
    ),
    (
        "Does Sanskrit appear correctly in downloaded files?",
        "Yes — Sanskrit verses appear in Devanāgarī script in the web UI, PDF, and DOCX. "
        "The app uses Noto fonts which support all Indian scripts. If Sanskrit appears as "
        "boxes or question marks in a downloaded file, open it with a font that supports "
        "Unicode (such as Noto Sans, Arial Unicode, or any modern system font)."
    ),
    (
        "Why is my PDF only showing a summary and not the full transcript?",
        "The Audio Summarizer always produces a summary — use the "
        "<b style='color:#b8a88a;'>Discourse Transcriber</b> page if you want the complete "
        "full transcript exported to PDF or DOCX."
    ),
])

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — DISCOURSE TRANSCRIBER
# ══════════════════════════════════════════════════════════════════════════════
faq_section("Discourse Transcriber", "📜", [
    (
        "What does the Custom Focus Prompt do?",
        "The custom focus prompt lets you give the AI specific instructions about what to "
        "highlight or pay attention to during transcription. For example:<br/><br/>"
        "• <i>Highlight the areas where Swamiji has particularly stressed a point</i><br/>"
        "• <i>Identify all places where other scriptural texts are referenced</i><br/>"
        "• <i>Flag all analogies and stories used to explain concepts</i><br/><br/>"
        "The AI will then mark these moments in the transcript with bold labels like "
        "<b>[KEY EMPHASIS]</b>, <b>[CROSS-REFERENCE: Bhagavatam]</b>, or <b>[ANALOGY]</b> "
        "so you can find them instantly."
    ),
    (
        "Is the Verse Range field required?",
        "No — the Verse Range field is completely optional. Leave it blank if you are "
        "transcribing a full discourse without a specific verse focus. Fill it in when "
        "you know the specific verses being covered (e.g. 'Verses 3–7' or 'Mantra 5') "
        "to help the AI provide more precise structuring."
    ),
    (
        "Why does transcription of long discourses take longer?",
        "Long discourses are processed in multiple steps — first transcribed by Whisper, "
        "then structured by Claude. A 2-hour discourse may take "
        "<b style='color:#b8a88a;'>8–12 minutes</b> in total. "
        "The progress bar shows which step the app is on. "
        "For very long recordings, consider splitting into 30–45 minute segments."
    ),
])

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — WISDOM EXTRACTOR
# ══════════════════════════════════════════════════════════════════════════════
faq_section("Wisdom Extractor", "💎", [
    (
        "What does 'verbatim' mean in the context of quote extraction?",
        "Verbatim means the AI extracts the teacher's "
        "<b style='color:#b8a88a;'>exact spoken words</b> — not a paraphrase or rewrite. "
        "Minor grammatical corrections may be applied (e.g. fixing subject-verb agreement) "
        "but the vocabulary, phrasing, and meaning are preserved faithfully. "
        "This ensures the quotes authentically represent the teacher's voice."
    ),
    (
        "What are the thematic tags assigned to each quote?",
        "Every quote is assigned one of eight Vedantic themes:<br/><br/>"
        "🔸 Self / Ātman &nbsp;·&nbsp; 🔸 Brahman / Non-duality &nbsp;·&nbsp; "
        "🔸 Ego &nbsp;·&nbsp; 🔸 Karma<br/>"
        "🔸 Devotion &nbsp;·&nbsp; 🔸 Detachment &nbsp;·&nbsp; "
        "🔸 Mind &nbsp;·&nbsp; 🔸 Knowledge"
    ),
    (
        "Can I use the YouTube titles and hashtags directly?",
        "Yes — they are ready to use. The YouTube title follows the format "
        "<i>Discourse | Topic | Core Insight</i> and is optimized for searchability. "
        "The hashtags combine general spiritual tags with discourse-specific concepts "
        "and are formatted for direct use on Instagram, YouTube, or X (Twitter)."
    ),
    (
        "What is the Focus Keywords field for?",
        "If you want the AI to prioritize certain themes when selecting quotes, "
        "enter keywords here — e.g. <i>surrender, ego, Ātman, instrument of God</i>. "
        "The AI will look specifically for the most powerful quotes on these themes "
        "while still extracting verbatim from the transcript."
    ),
])

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — REFLECTION & NOTES
# ══════════════════════════════════════════════════════════════════════════════
faq_section("Personal Reflection & Notes", "🪷", [
    (
        "Can I add my own notes or reflections to the output?",
        "Yes — every output page has a "
        "<b style='color:#b8a88a;'>My Reflections</b> section at the bottom where you "
        "can type your own notes, questions, or insights. When you download the PDF or DOCX, "
        "your reflections are included at the end of the document — creating a complete "
        "personal study record that combines the AI output with your own contemplation."
    ),
    (
        "Why is a reflection section important?",
        "The three stages of Vedantic learning are "
        "<b style='color:#c9a96e;'>Śravaṇa</b> (listening), "
        "<b style='color:#c9a96e;'>Manana</b> (reflection), and "
        "<b style='color:#c9a96e;'>Nididhyāsana</b> (deep contemplation). "
        "This app supports all three — transcription and summarization support śravaṇa, "
        "the structured output supports manana, and the reflection section supports "
        "nididhyāsana by giving you a space to record your own inquiry and understanding."
    ),
    (
        "Are my reflections saved between sessions?",
        "No — like all content in the app, reflections exist only in your current browser "
        "session. Please download your document before closing the tab to preserve your notes. "
        "This is intentional — no personal data is ever stored on any server."
    ),
])

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — TROUBLESHOOTING
# ══════════════════════════════════════════════════════════════════════════════
faq_section("Troubleshooting", "🔧", [
    (
        "The app shows an 'Oh no' error — what do I do?",
        "1. Click the <b>⋮ (three dots)</b> in the top right of the Streamlit app<br/>"
        "2. Select <b>Reboot app</b><br/>"
        "3. Wait 30–60 seconds for it to restart<br/>"
        "4. Re-enter your API keys on the Home page (they clear on reboot)<br/><br/>"
        "If the error persists, try refreshing the page or clearing your browser cache."
    ),
    (
        "My transcription came out garbled or incorrect — why?",
        "Transcription quality depends on audio quality. For best results:<br/><br/>"
        "• Use clear audio with minimal background noise<br/>"
        "• Avoid recordings with heavy echo or reverb<br/>"
        "• MP3 or M4A at 128kbps or higher works best<br/>"
        "• If the speaker has a strong accent, the AI adjusts — but very noisy recordings "
        "may produce errors in Sanskrit terms specifically<br/>"
        "• You can always edit the raw transcript in the Raw tab before re-processing"
    ),
    (
        "I entered my API key but it says it's not working — what should I check?",
        "• Make sure you copied the <b>complete</b> key (they are long strings)<br/>"
        "• Anthropic keys start with <b>sk-ant-</b><br/>"
        "• OpenAI keys start with <b>sk-</b><br/>"
        "• Check that your account has available credits<br/>"
        "• Make sure there are no extra spaces before or after the key when pasting"
    ),
    (
        "The summary is in English even though I selected a different language — why?",
        "The transcription is always done in English first (Whisper works best in English). "
        "The translation to your chosen language happens in a second step. "
        "If translation didn't occur, try re-running with your language selected — "
        "it may have been a temporary API timeout."
    ),
    (
        "Can I use this on my phone?",
        "Yes — the app is accessible on mobile browsers. However, audio file uploads "
        "work best on desktop. On mobile, you can paste transcripts directly into the "
        "text input fields for summarization and quote extraction."
    ),
])

# ── Closing ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style='max-width:700px; margin: 2rem auto 0;'>
<div style='background:#0d0d0d; border:1px solid #1e1e1e; border-radius:12px;
padding:1.6rem 2rem; text-align:center;'>
    <div style='font-family:Cormorant Garamond,serif; font-style:italic;
    font-size:1rem; color:#888; line-height:1.9;'>
    Still have a question? Reach out at
    <a href="mailto:vedantavani.manana@gmail.com"
    style="color:#c9a96e; text-decoration:none; border-bottom:1px dashed #c9a96e;">
    vedantavani.manana@gmail.com</a>
    </div>
</div>
</div>
<div style="text-align:center; padding: 2rem 0 1rem;">
    <div style="font-size:1.2rem; letter-spacing:8px;">🪷 🕉️ 🪷</div>
</div>
""", unsafe_allow_html=True)
