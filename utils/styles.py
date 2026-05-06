SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400;1,600&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0a !important;
    color: #e8e0d4 !important;
}

section[data-testid="stSidebar"] {
    background: #111111 !important;
    border-right: 1px solid #1e1e1e !important;
}
section[data-testid="stSidebar"] * { color: #b8a88a !important; }
section[data-testid="stSidebar"] a:hover { color: #c9a96e !important; }

.main, .block-container, [data-testid="stAppViewContainer"] {
    background-color: #0a0a0a !important;
}
.main .block-container {
    padding: 2rem 3rem;
    max-width: 860px;
    margin: 0 auto;
}

.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    border-bottom: 1px solid #1e1e1e;
}
.hero h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3rem;
    font-weight: 600;
    color: #e8e0d4;
    margin: 0.3rem 0;
    letter-spacing: -0.5px;
}
.hero .accent { color: #c9a96e; }
.hero .subtitle {
    font-size: 0.88rem;
    color: #555;
    font-weight: 300;
    letter-spacing: 0.5px;
    margin-bottom: 0.6rem;
}

.about-box {
    background: #111;
    border: 1px solid #2a2a2a;
    border-left: 3px solid #c9a96e;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    font-size: 0.9rem;
    color: #888;
    line-height: 1.8;
    margin: 1rem 0;
}

.step-label {
    display: inline-block;
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.75rem;
    color: #c9a96e;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

.output-box {
    background: #111;
    border: 1px solid #1e1e1e;
    border-radius: 10px;
    padding: 1.5rem;
    font-size: 0.92rem;
    line-height: 1.9;
    color: #c8bfb0;
}

.file-pill {
    display: inline-block;
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78rem;
    color: #888;
    margin: 2px 4px;
}

.stButton > button {
    background: #161616 !important;
    color: #c9a96e !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
    padding: 0.5rem 1.4rem !important;
    font-weight: 400 !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #1e1e1e !important;
    border-color: #c9a96e !important;
}

.stDownloadButton > button {
    background: #161616 !important;
    color: #888 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}
.stDownloadButton > button:hover {
    border-color: #c9a96e !important;
    color: #c9a96e !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #111 !important;
    border: 1px solid #2a2a2a !important;
    color: #e8e0d4 !important;
    border-radius: 8px !important;
}
.stSelectbox > div > div {
    background: #111 !important;
    border: 1px solid #2a2a2a !important;
    color: #e8e0d4 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #111;
    border-radius: 10px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #555 !important;
    background: transparent !important;
    border-radius: 8px !important;
}
.stTabs [aria-selected="true"] {
    background: #1e1e1e !important;
    color: #c9a96e !important;
}

.stProgress > div > div { background: #c9a96e !important; }

.streamlit-expanderHeader {
    background: #111 !important;
    color: #888 !important;
    border-radius: 8px !important;
}

.quote-block {
    text-align: center;
    padding: 1.5rem 2rem;
    border-top: 1px solid #1e1e1e;
    border-bottom: 1px solid #1e1e1e;
    margin: 1rem 0;
}
.quote-text {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 1.1rem;
    color: #c9a96e;
    line-height: 1.9;
    margin-bottom: 0.5rem;
}

/* Home button fix */
[data-testid="stSidebarNav"] li:first-child a span:last-child::before {
    content: "Home";
    position: absolute;
}
[data-testid="stSidebarNav"] li:first-child a span:last-child {
    font-size: 0;
    position: relative;
}

.nav-card {
    background: #111;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
}
.nav-card:hover {
    border-color: #c9a96e;
    background: #161616;
}
</style>
"""
