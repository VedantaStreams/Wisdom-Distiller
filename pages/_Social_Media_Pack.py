import streamlit as st
import sys
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.styles import SHARED_CSS
from utils.helpers import make_pdf, make_docx

st.set_page_config(
    page_title="Social Media Pack · Wisdom Distiller",
    page_icon="📲",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Admin password gate — must come before ANYTHING else ──────────────────────
_correct = st.secrets.get("SOCIAL_PACK_PASSWORD", "")

if "smp_authenticated" not in st.session_state:
    st.session_state["smp_authenticated"] = False

if not st.session_state["smp_authenticated"]:
    st.markdown("""
    <div style='text-align:center;padding:4rem 1rem 2rem;'>
        <div style='font-size:2.5rem;margin-bottom:1rem;'>🔒</div>
        <div style='font-family:Cormorant Garamond,serif;font-size:1.4rem;
        color:#e8e0d4;margin-bottom:0.5rem;'>Restricted Page</div>
        <div style='font-size:0.82rem;color:#555;margin-bottom:1.5rem;'>
        Enter your access code to continue.</div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        pwd_input = st.text_input(
            "Access code", type="password",
            key="smp_pwd_input",
            placeholder="Enter access code…",
            label_visibility="collapsed"
        )
        if st.button("🔓 Unlock", use_container_width=True, key="smp_unlock"):
            if pwd_input == _correct:
                st.session_state["smp_authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect access code. Please try again.")
    st.stop()

st.markdown(SHARED_CSS, unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    try:
        st.page_link("app.py", label="🏠 Home")
    except Exception:
        if st.button("🏠 Home", key="home_btn_smp"):
            st.switch_page("app.py")
    st.markdown("<hr style='border-color:#1e1e1e; margin:0.3rem 0 0.8rem;'/>",
                unsafe_allow_html=True)

# ── API key ────────────────────────────────────────────────────────────────────
anthropic_key = st.session_state.get("anthropic_key", "")
if not anthropic_key:
    try:
        anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>📲 Social Media <span class="accent">Pack</span></h1>
    <p class="subtitle">
        Quote · Theme · Canva card · Instagram · Reflection · Image prompt · Hashtags
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="about-box">
    Turn any discourse quote into a complete social media pack — ready for
    Instagram, WhatsApp, and Canva. Run the
    <b style='color:#c9a96e;'>Wisdom Extractor</b> first and your quotes will
    appear automatically, or paste any quote below.
    Each pack is generated individually so every quote gets content tuned to its
    specific teaching.
</div>
""", unsafe_allow_html=True)

# ── Claude call ────────────────────────────────────────────────────────────────
SOCIAL_PROMPT = """You are a devoted student of Vedānta and an experienced spiritual
content creator deeply familiar with Chinmaya Mission, Advaita Vedānta, and the
tradition of the Bhagavad Gītā and Upaniṣads.

Given a verbatim quote from a discourse, generate a complete social media content pack.
Every element must be authentically devotional — never commercial, never shallow.
The tone is warm, inviting, and rooted in the teaching.

CRITICAL SANSKRIT RULE: Any Sanskrit verse or term MUST appear in Devanāgarī script.
Never transliterate Sanskrit verses into Roman script.

Generate exactly these seven fields:

1. QUOTE: The verbatim quote exactly as given — do not alter a single word.

2. THEME: One of: Self / Ātman | Brahman / Non-duality | Ego | Karma |
   Devotion | Detachment | Mind | Knowledge

3. CANVA_CARD: Text for a Canva quote card — 1–3 lines maximum, beautifully
   formatted for display. May be a slightly condensed or poetic version of the
   quote if needed for visual impact. If the quote contains a Sanskrit verse,
   display it in Devanāgarī followed by its meaning.

4. INSTAGRAM_CAPTION: A warm, engaging Instagram caption. Structure:
   - Opening line that draws the reader in (not the quote itself)
   - The quote on its own line, in quotes
   - 2–3 sentences of gentle reflection connecting the teaching to daily life
   - A closing line that invites the reader to pause or reflect
   Maximum 8 lines total.

5. REFLECTION_QUESTION: One deep, open-ended question for the reader to sit
   with — a genuine Manana prompt. Should arise naturally from this specific
   quote. Not a yes/no question. One sentence only.

6. IMAGE_PROMPT: A detailed prompt for an AI image generator (Midjourney /
   DALL-E style) to create a visual that evokes the mood and meaning of this
   quote. Should describe: subject, setting, lighting, color palette, artistic
   style. Vedantic and devotional in character — no people's faces.
   2–4 sentences.

7. HASHTAGS: 10–14 hashtags. Mix of: broad spiritual (#Vedanta #Advaita
   #Spirituality #SelfKnowledge #Mindfulness #Meditation), Chinmaya-specific
   (#ChinmayaMission #SwamijisTeaching), and quote-specific concept tags.
   No spaces within hashtags.

OUTPUT — STRICT JSON ONLY, no markdown fences, no preamble:
{
  "quote": "exact quote as given",
  "theme": "one theme",
  "canva_card": "1-3 line card text",
  "instagram_caption": "full instagram caption",
  "reflection_question": "one deep question",
  "image_prompt": "detailed image generation prompt",
  "hashtags": ["#Vedanta", "#Advaita"]
}"""


def generate_pack(quote: str, speaker: str, scripture: str,
                  anthropic_key: str) -> dict:
    import anthropic as _anthropic
    client = _anthropic.Anthropic(api_key=anthropic_key)

    context = ""
    if speaker:
        context += f"Speaker: {speaker}\n"
    if scripture:
        context += f"Scripture: {scripture}\n"

    user_content = (
        f"{context}\nQuote:\n\"{quote}\""
    )

    msg = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2000,
        system=SOCIAL_PROMPT,
        messages=[{"role": "user", "content": user_content}]
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start != -1 and end > start:
            cleaned = re.sub(r',\s*}', '}', raw[start:end])
            cleaned = re.sub(r',\s*]', ']', cleaned)
            return json.loads(cleaned)
        raise


# ── Step 1 — Quote source ──────────────────────────────────────────────────────
st.markdown("<div class='step-label'>Step 1 — Choose Quotes</div>",
            unsafe_allow_html=True)

# Check if Wisdom Extractor result is in session
qs_result = st.session_state.get("qs_result", {})
extractor_quotes = []

if qs_result:
    if qs_result.get("grouped") and qs_result.get("quote_groups"):
        for group in qs_result["quote_groups"]:
            extractor_quotes.extend(group.get("quotes", []))
    else:
        extractor_quotes = qs_result.get("quotes", [])

tab_extractor, tab_manual = st.tabs(
    ["💎 From Wisdom Extractor", "✍️ Enter Quote Manually"]
)

selected_quotes = []   # list of dicts: {text, theme, speaker, scripture}

with tab_extractor:
    if not extractor_quotes:
        st.markdown(
            "<div style='background:#111;border:1px solid #2a2a2a;"
            "border-left:3px solid #c9a96e;border-radius:10px;"
            "padding:1.1rem 1.4rem;font-size:0.85rem;color:#888;'>"
            "No quotes found from the Wisdom Extractor yet.<br/>"
            "Run the <b style='color:#c9a96e;'>💎 Wisdom Extractor</b> first, "
            "then come back here — your quotes will appear automatically.<br/><br/>"
            "Or switch to the <b style='color:#b8a88a;'>✍️ Enter Quote Manually</b> "
            "tab to paste any quote directly."
            "</div>",
            unsafe_allow_html=True
        )
    else:
        speaker_ex  = qs_result.get("speaker", "")
        scripture_ex = qs_result.get("scripture", "")

        st.markdown(
            f"<div style='font-size:0.82rem;color:#888;margin-bottom:0.8rem;'>"
            f"Found <b style='color:#c9a96e;'>{len(extractor_quotes)} quotes</b>"
            f"{(' from ' + speaker_ex) if speaker_ex else ''}"
            f"{(' · ' + scripture_ex) if scripture_ex else ''}. "
            f"Select the ones you want to generate packs for.</div>",
            unsafe_allow_html=True
        )

        # Select all / clear all
        sc1, sc2 = st.columns(2)
        with sc1:
            if st.button("✅ Select all", key="smp_select_all"):
                for i in range(len(extractor_quotes)):
                    st.session_state[f"smp_chk_{i}"] = True
        with sc2:
            if st.button("✖️ Clear all", key="smp_clear_all"):
                for i in range(len(extractor_quotes)):
                    st.session_state[f"smp_chk_{i}"] = False

        st.markdown("<br/>", unsafe_allow_html=True)

        for i, q in enumerate(extractor_quotes):
            theme = q.get("theme", "")
            text  = q.get("text", "")
            checked = st.checkbox(
                f"**{theme}** — *\"{text[:90]}{'…' if len(text) > 90 else ''}\"*",
                key=f"smp_chk_{i}",
                value=st.session_state.get(f"smp_chk_{i}", False)
            )
            if checked:
                selected_quotes.append({
                    "text":      text,
                    "theme":     theme,
                    "speaker":   speaker_ex,
                    "scripture": scripture_ex,
                })

with tab_manual:
    st.markdown(
        "<div style='font-size:0.82rem;color:#888;margin-bottom:0.5rem;'>"
        "Paste any quote from any discourse — from Swamiji, a scriptural verse, "
        "or any teaching you want to turn into a social media pack."
        "</div>",
        unsafe_allow_html=True
    )
    manual_quote = st.text_area(
        "Quote",
        height=120,
        placeholder="Paste the quote here — exactly as spoken or written…",
        key="smp_manual_quote",
        label_visibility="collapsed"
    )
    m1, m2 = st.columns(2)
    with m1:
        manual_speaker = st.text_input(
            "🎙️ Speaker (optional)",
            placeholder="e.g. Swami Tejomayananda",
            key="smp_manual_speaker"
        )
    with m2:
        manual_scripture = st.text_input(
            "📚 Scripture / Topic (optional)",
            placeholder="e.g. Bhagavad Gītā Ch.12",
            key="smp_manual_scripture"
        )
    if manual_quote.strip():
        selected_quotes.append({
            "text":      manual_quote.strip(),
            "theme":     "",
            "speaker":   manual_speaker.strip(),
            "scripture": manual_scripture.strip(),
        })

# ── Step 2 — Generate ─────────────────────────────────────────────────────────
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown("<div class='step-label'>Step 2 — Generate Packs</div>",
            unsafe_allow_html=True)

if selected_quotes:
    st.markdown(
        f"<div style='font-size:0.85rem;color:#888;margin-bottom:0.8rem;'>"
        f"Ready to generate <b style='color:#c9a96e;'>"
        f"{len(selected_quotes)} pack{'s' if len(selected_quotes) > 1 else ''}</b>."
        f"</div>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<div style='font-size:0.85rem;color:#555;margin-bottom:0.8rem;'>"
        "Select quotes above or enter one manually to get started.</div>",
        unsafe_allow_html=True
    )

generate_btn = st.button(
    "📲 Generate Social Media Pack" + ("s" if len(selected_quotes) > 1 else ""),
    key="smp_generate",
    use_container_width=True,
    disabled=(not selected_quotes or not anthropic_key)
)

if not anthropic_key:
    st.warning("⚠️ Please enter your Anthropic API key on the Home page.")

if generate_btn and selected_quotes and anthropic_key:
    packs = []
    progress = st.progress(0)
    status   = st.empty()
    total    = len(selected_quotes)

    for idx, q in enumerate(selected_quotes):
        status.markdown(
            f"**Generating pack {idx + 1} of {total}…** "
            f"*\"{q['text'][:60]}…\"*"
        )
        try:
            pack = generate_pack(
                q["text"], q["speaker"], q["scripture"], anthropic_key
            )
            pack["_speaker"]   = q["speaker"]
            pack["_scripture"] = q["scripture"]
            packs.append(pack)
        except Exception as e:
            packs.append({"_error": str(e), "_quote": q["text"]})
        progress.progress(int((idx + 1) / total * 100))

    status.success(
        f"✅ {len([p for p in packs if '_error' not in p])} pack"
        f"{'s' if total > 1 else ''} generated!"
    )
    st.session_state["smp_packs"] = packs


# ── Results ────────────────────────────────────────────────────────────────────
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

FIELD_ICONS = {
    "quote":               ("💬", "Quote"),
    "theme":               ("🏷️", "Theme"),
    "canva_card":          ("🎨", "Canva Card Text"),
    "instagram_caption":   ("📸", "Instagram Caption"),
    "reflection_question": ("🪷", "Reflection Question"),
    "image_prompt":        ("🖼️", "Image Prompt"),
    "hashtags":            ("🔖", "Hashtags"),
}


def render_pack(pack: dict, index: int):
    if "_error" in pack:
        st.error(f"Pack {index + 1} failed: {pack['_error']}")
        st.markdown(f"*Quote: \"{pack.get('_quote','')}\"*")
        return

    theme = pack.get("theme", "")
    color = THEME_COLORS.get(theme, "#c9a96e")
    speaker   = pack.get("_speaker", "")
    scripture = pack.get("_scripture", "")

    # Pack header
    meta = " · ".join(filter(None, [speaker, scripture]))
    st.markdown(
        f"<div style='background:#0d0d0d;border:1px solid #2a2a2a;"
        f"border-top:4px solid {color};border-radius:14px;"
        f"padding:1.4rem 1.8rem;margin-bottom:0.5rem;'>"
        f"<div style='font-size:0.68rem;color:{color};text-transform:uppercase;"
        f"letter-spacing:1px;margin-bottom:0.5rem;font-weight:600;'>"
        f"📲 Social Media Pack {index + 1}"
        f"{'  ·  ' + meta if meta else ''}</div>"
        f"<div style='font-family:Cormorant Garamond,serif;font-style:italic;"
        f"font-size:1.05rem;color:#e8e0d4;line-height:1.8;'>"
        f"\"{pack.get('quote','')}\"</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    # Seven fields
    fields = [
        ("theme",               pack.get("theme", "")),
        ("canva_card",          pack.get("canva_card", "")),
        ("instagram_caption",   pack.get("instagram_caption", "")),
        ("reflection_question", pack.get("reflection_question", "")),
        ("image_prompt",        pack.get("image_prompt", "")),
        ("hashtags",            pack.get("hashtags", [])),
    ]

    for field_key, value in fields:
        icon, label = FIELD_ICONS.get(field_key, ("•", field_key))

        if field_key == "hashtags" and isinstance(value, list):
            tags_html = " ".join(
                f"<span style='background:#161616;border:1px solid #2a2a2a;"
                f"border-radius:20px;padding:2px 10px;font-size:0.75rem;"
                f"color:#c9a96e;margin:2px;display:inline-block;'>{h}</span>"
                for h in value
            )
            st.markdown(
                f"<div style='background:#111;border:1px solid #1e1e1e;"
                f"border-radius:10px;padding:1rem 1.3rem;margin-bottom:0.6rem;'>"
                f"<div style='font-size:0.68rem;color:{color};text-transform:uppercase;"
                f"letter-spacing:0.8px;margin-bottom:0.5rem;font-weight:600;'>"
                f"{icon} {label}</div>"
                f"<div style='margin-top:0.2rem;'>{tags_html}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        elif field_key == "theme":
            st.markdown(
                f"<div style='background:#111;border:1px solid #1e1e1e;"
                f"border-radius:10px;padding:0.7rem 1.3rem;margin-bottom:0.6rem;"
                f"display:inline-block;'>"
                f"<span style='font-size:0.68rem;color:{color};text-transform:uppercase;"
                f"letter-spacing:0.8px;font-weight:600;'>{icon} {label}: </span>"
                f"<span style='font-size:0.85rem;color:#e8e0d4;'>{value}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
        elif field_key == "instagram_caption":
            # Render with line breaks preserved
            caption_html = value.replace("\n", "<br/>")
            st.markdown(
                f"<div style='background:#111;border:1px solid #1e1e1e;"
                f"border-radius:10px;padding:1rem 1.3rem;margin-bottom:0.6rem;'>"
                f"<div style='font-size:0.68rem;color:{color};text-transform:uppercase;"
                f"letter-spacing:0.8px;margin-bottom:0.6rem;font-weight:600;'>"
                f"{icon} {label}</div>"
                f"<div style='font-size:0.87rem;color:#d4c9b8;line-height:1.8;'>"
                f"{caption_html}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        elif field_key == "canva_card":
            card_html = value.replace("\n", "<br/>")
            st.markdown(
                f"<div style='background:#111;border:1px solid #1e1e1e;"
                f"border-left:3px solid {color};"
                f"border-radius:10px;padding:1rem 1.3rem;margin-bottom:0.6rem;'>"
                f"<div style='font-size:0.68rem;color:{color};text-transform:uppercase;"
                f"letter-spacing:0.8px;margin-bottom:0.6rem;font-weight:600;'>"
                f"{icon} {label}</div>"
                f"<div style='font-family:Cormorant Garamond,serif;font-style:italic;"
                f"font-size:1rem;color:#e8e0d4;line-height:1.9;'>"
                f"{card_html}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='background:#111;border:1px solid #1e1e1e;"
                f"border-radius:10px;padding:1rem 1.3rem;margin-bottom:0.6rem;'>"
                f"<div style='font-size:0.68rem;color:{color};text-transform:uppercase;"
                f"letter-spacing:0.8px;margin-bottom:0.5rem;font-weight:600;'>"
                f"{icon} {label}</div>"
                f"<div style='font-size:0.87rem;color:#d4c9b8;line-height:1.75;'>"
                f"{value}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    # ── Copy-friendly text area + download ─────────────────────────────────
    hashtags_str = " ".join(pack.get("hashtags", []))
    export_lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  SOCIAL MEDIA PACK",
        f"  {meta}" if meta else "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "💬 QUOTE",
        f'"{pack.get("quote","")}"',
        "",
        f"🏷️ THEME: {pack.get('theme','')}",
        "",
        "🎨 CANVA CARD TEXT",
        pack.get("canva_card", ""),
        "",
        "📸 INSTAGRAM CAPTION",
        pack.get("instagram_caption", ""),
        "",
        "🪷 REFLECTION QUESTION",
        pack.get("reflection_question", ""),
        "",
        "🖼️ IMAGE PROMPT",
        pack.get("image_prompt", ""),
        "",
        "🔖 HASHTAGS",
        hashtags_str,
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    export_text = "\n".join(filter(lambda x: x is not None, export_lines))

    with st.expander("📋 Copy-friendly text", expanded=False):
        st.text_area(
            "Copy the full pack",
            value=export_text,
            height=300,
            key=f"smp_copy_{index}",
            label_visibility="collapsed"
        )

    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            "⬇️ TXT",
            data=export_text,
            file_name=f"social_pack_{index + 1}.txt",
            mime="text/plain",
            key=f"smp_dl_txt_{index}"
        )
    with dl2:
        try:
            title = f"Social Media Pack — {pack.get('theme','')}"
            pdf = make_pdf(title, export_text,
                           speaker=speaker, topic=pack.get("theme",""),
                           scripture=scripture)
            st.download_button(
                "⬇️ PDF",
                data=pdf,
                file_name=f"social_pack_{index + 1}.pdf",
                mime="application/pdf",
                key=f"smp_dl_pdf_{index}"
            )
        except Exception as e:
            st.caption(f"PDF: {e}")

    st.markdown("<hr style='border-color:#1e1e1e;margin:1.5rem 0;'/>",
                unsafe_allow_html=True)


# ── Render all packs ───────────────────────────────────────────────────────────
packs = st.session_state.get("smp_packs", [])
if packs:
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='step-label'>"
        f"{'Pack' if len(packs) == 1 else str(len(packs)) + ' Packs'} Generated</div>",
        unsafe_allow_html=True
    )

    # Bulk download all packs as one TXT
    if len(packs) > 1:
        all_lines = []
        for i, p in enumerate(packs):
            if "_error" not in p:
                hashtags_str = " ".join(p.get("hashtags", []))
                all_lines += [
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    f"  PACK {i+1}  ·  {p.get('theme','')}",
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    "",
                    f'💬 "{p.get("quote","")}"',
                    "",
                    f"🎨 CANVA CARD\n{p.get('canva_card','')}",
                    "",
                    f"📸 INSTAGRAM CAPTION\n{p.get('instagram_caption','')}",
                    "",
                    f"🪷 REFLECTION\n{p.get('reflection_question','')}",
                    "",
                    f"🖼️ IMAGE PROMPT\n{p.get('image_prompt','')}",
                    "",
                    f"🔖 {hashtags_str}",
                    "",
                ]
        st.download_button(
            f"⬇️ Download all {len(packs)} packs as TXT",
            data="\n".join(all_lines),
            file_name="social_media_packs.txt",
            mime="text/plain",
            key="smp_dl_all",
            use_container_width=True
        )
        st.markdown("<br/>", unsafe_allow_html=True)

    for i, pack in enumerate(packs):
        render_pack(pack, i)

    if st.button("🔄 Clear and start over", key="smp_clear"):
        st.session_state.pop("smp_packs", None)
        st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;padding:1.5rem 1rem 2rem;'>"
    "<div style='font-family:Cormorant Garamond,serif;font-style:italic;"
    "font-size:0.95rem;color:#555;line-height:1.9;max-width:480px;margin:0 auto;'>"
    "May every word shared be an offering — and every reader, a seeker."
    "</div></div>",
    unsafe_allow_html=True
)
