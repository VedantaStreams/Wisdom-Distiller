"""
Shared 'Additional Focus / Custom Prompt' component.

Used by the Audio Summarizer and Video Summarizer pages.
Renders a preset dropdown (+ Add button, pills, clear) and a free-text box,
and returns the combined focus instructions as a single string.
"""

import streamlit as st

FOCUS_PRESETS = {
    "— Select a focus preset —": "",
    # Emphasis & structure
    "🔆 Key emphasized points":
        "Give special prominence to the points the speaker stressed or repeated.",
    "📚 Cross-scriptural references":
        "Identify all references to other scriptures or texts and include them with context.",
    "🪔 Analogies and stories":
        "Capture every analogy, story, and example used, and what each illustrates.",
    "🕉️ Sanskrit terms with meanings":
        "Include all important Sanskrit terms with their meanings.",
    "❓ Questions & answers":
        "Identify any question-and-answer exchanges and summarize each question with its answer.",
    # Depth of teaching
    "✨ Liberation / mokṣa teachings":
        "Highlight every teaching specifically about liberation, mokṣa, or mukti.",
    "🧘 Practical guidance for daily life":
        "Emphasize the practical applications and daily-life guidance from the teaching.",
    "🌉 Connections to other talks/chapters":
        "Note connections the speaker draws to other chapters, texts, or earlier talks.",
    # Audience & sharing
    "📱 Top 5 quotable statements":
        "Include the 5 most powerful, self-contained, quotable statements from this discourse.",
    "👶 Simplified for beginners":
        "Explain the concepts simply, suitable for someone new to Vedānta.",
}


def render_focus_prompt(prefix: str) -> str:
    """Render the focus-prompt UI and return the combined instruction string.

    `prefix` keeps widget keys unique per page (e.g. "aud", "vid").
    """
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown(
        "<div class='step-label'>Additional Focus / Custom Prompt (optional)</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='font-size:0.82rem;color:#666;margin-bottom:0.5rem;'>"
        "Direct the AI's attention — choose presets, add your own instructions, "
        "or both. The summary will reflect these focus areas as clean flowing text."
        "</div>",
        unsafe_allow_html=True
    )

    col_preset, col_add = st.columns([3, 1])
    with col_preset:
        selected_preset = st.selectbox(
            "📋 Choose a focus preset",
            options=list(FOCUS_PRESETS.keys()),
            key=f"{prefix}_preset_select",
            help="Select a preset, then click ➕ Add. You can stack several."
        )
    with col_add:
        st.markdown("<br/>", unsafe_allow_html=True)
        add_pressed = st.button("➕ Add", key=f"{prefix}_add_preset",
                                use_container_width=True)

    acc_key = f"{prefix}_accumulated_prompt"
    if acc_key not in st.session_state:
        st.session_state[acc_key] = ""

    if add_pressed and FOCUS_PRESETS.get(selected_preset):
        preset_text = FOCUS_PRESETS[selected_preset]
        current = st.session_state[acc_key].strip()
        if preset_text not in current:
            st.session_state[acc_key] = (
                (current + "\n" + preset_text) if current else preset_text
            )

    accumulated = st.session_state.get(acc_key, "")
    if accumulated:
        pills = [p.strip() for p in accumulated.split("\n") if p.strip()]
        pills_html = " ".join(
            f"<span style='background:#161616;border:1px solid #c9a96e;"
            f"border-radius:20px;padding:3px 10px;font-size:0.75rem;"
            f"color:#c9a96e;margin:2px;display:inline-block;'>"
            f"✓ {p[:60]}{'…' if len(p) > 60 else ''}</span>"
            for p in pills
        )
        st.markdown(
            f"<div style='margin:0.4rem 0 0.2rem;'>{pills_html}</div>",
            unsafe_allow_html=True
        )
        if st.button("🗑️ Clear all presets", key=f"{prefix}_clear_presets"):
            st.session_state[acc_key] = ""
            st.rerun()

    st.markdown(
        "<div style='font-size:0.78rem;color:#555;margin:0.4rem 0 0.3rem;'>"
        "Add your own instructions below, or leave blank to use presets only.</div>",
        unsafe_allow_html=True
    )
    custom_extra = st.text_area(
        "Additional custom instructions",
        key=f"{prefix}_custom_prompt",
        height=90,
        placeholder=(
            "Add your own specific instructions here...\n"
            "e.g. Pay special attention to how Swamiji connects this teaching to daily life."
        ),
        label_visibility="collapsed"
    )

    _preset_part = st.session_state.get(acc_key, "").strip()
    _custom_part = custom_extra.strip()
    return "\n".join(filter(None, [_preset_part, _custom_part]))
