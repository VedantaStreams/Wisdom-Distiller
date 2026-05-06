SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400;1,600&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #fdf6ee !important;
    color: #2d1a0e !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #f5e6d3 !important;
    border-right: 1px solid #d4a96e !important;
}
section[data-testid="stSidebar"] * { color: #2d1a0e !important; }
section[data-testid="stSidebar"] a { color: #7a1a28 !important; }

/* Main background */
.main, .block-container, [data-testid="stAppViewContainer"] {
    background-color: #fdf6ee !important;
}
.main .block-container {
    padding: 2rem 3rem;
    max-width: 860px;
    margin: 0 auto;
}

/* Hero */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    border-bottom: 2px solid #c9a96e;
}
.hero h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3rem;
    font-weight: 600;
    color: #2d1a0e;
    margin: 0.3rem 0;
    letter-spacing: -0.5px;
}
.hero .accent { color: #7a1a28; }
.hero .subtitle {
    font-size: 0.88rem;
    color: #7a5c44;
    font-weight: 300;
    letter-spacing: 0.5px;
    margin-bottom: 0.6rem;
}
.hero .om { width: 56px; opacity: 0.85; }

/* About box */
.about-box {
    background: #fff8f0;
    border: 1px solid #e8c99a;
    border-left: 4px solid #c9a96e;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    font-size: 0.9rem;
    color: #2d1a0e;
    line-height: 1.8;
    margin: 1rem 0;
}

/* Step labels */
.step-label {
    display: inline-block;
    background: #fff0dc;
    border: 1px solid #c9a96e;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.75rem;
    color: #7a1a28;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

/* Output box */
.output-box {
    background: #fff8f0;
    border: 1px solid #e8c99a;
    border-radius: 10px;
    padding: 1.5rem;
    font-size: 0.92rem;
    line-height: 1.9;
    color: #2d1a0e;
}

/* File pills */
.file-pill {
    display: inline-block;
    background: #fff0dc;
    border: 1px solid #e8c99a;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78rem;
    color: #4a2c1a;
    margin: 2px 4px;
}

/* Buttons */
.stButton > button {
    background: #c9a96e !important;
    color: #2d1a0e !important;
    border: 1px solid #b8935a !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
    padding: 0.5rem 1.4rem !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    background: #b8935a !important;
    color: #fff !important;
}

/* Download buttons */
.stDownloadButton > button {
    background: #fff0dc !important;
    color: #7a1a28 !important;
    border: 1px solid #c9a96e !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
.stDownloadButton > button:hover {
    background: #c9a96e !important;
    color: #2d1a0e !important;
}

/* Input fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: #fff8f0 !important;
    border: 1px solid #d4a96e !important;
    color: #2d1a0e !important;
    border-radius: 8px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #fff0dc;
    border-radius: 10px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #7a5c44 !important;
    background: transparent !important;
    border-radius: 8px !important;
}
.stTabs [aria-selected="true"] {
    background: #c9a96e !important;
    color: #2d1a0e !important;
    font-weight: 600 !important;
}

/* Progress bar */
.stProgress > div > div {
    background: #c9a96e !important;
}

/* Success/warning/error boxes */
.stSuccess { background: #f0fdf0 !important; color: #1a5c1a !important; }
.stWarning { background: #fffbf0 !important; color: #7a5c00 !important; }
.stError   { background: #fff0f0 !important; color: #7a1a1a !important; }

/* Quote block */
.quote-block {
    text-align: center;
    padding: 1.5rem 2rem;
    border-top: 1px solid #e8c99a;
    border-bottom: 1px solid #e8c99a;
    margin: 1rem 0;
}
.quote-text {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 1.1rem;
    color: #7a1a28;
    line-height: 1.9;
    margin-bottom: 0.5rem;
}

/* Bio avatar placeholder */
.bio-avatar-placeholder {
    width: 110px; height: 110px;
    border-radius: 50%;
    background: #f0e0c8;
    border: 3px solid #c9a96e;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 0.6rem;
    font-size: 1.4rem; font-weight: 600; color: #7a1a28;
}

/* Home sidebar label fix */
[data-testid="stSidebarNav"] li:first-child a span:last-child::before {
    content: "Home";
    position: absolute;
}
[data-testid="stSidebarNav"] li:first-child a span:last-child {
    font-size: 0;
    position: relative;
}

/* Expander */
.streamlit-expanderHeader {
    background: #fff0dc !important;
    color: #7a1a28 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
</style>
"""

