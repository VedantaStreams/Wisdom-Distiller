SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400;1,600&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background-color: #0a0a0a; color: #e8e0d4; }
h1, h2, h3 { font-family: 'Cormorant Garamond', serif; color: #e8e0d4; }

.hero {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
    border-bottom: 1px solid #2a2a2a;
    margin-bottom: 0.5rem;
}
.hero img.om {
    width: 70px; height: 70px;
    object-fit: contain; margin-bottom: 0.4rem;
    filter: drop-shadow(0 0 18px rgba(201,169,110,0.5));
}
.hero h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3.8rem; font-weight: 600;
    letter-spacing: 1px; color: #e8e0d4; margin: 0 0 0.2rem;
}
.hero .subtitle { font-size: 0.88rem; color: #aaa; font-weight: 300; letter-spacing: 0.5px; margin-bottom: 0.6rem; }
.accent { color: #c9a96e; }

.quote-block { text-align: center; padding: 0.8rem 2rem 1.2rem; border-bottom: 1px solid #1e1e1e; margin-bottom: 1.5rem; }
.quote-text { font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 1.05rem; color: #c9a96e; line-height: 1.7; }
.quote-author { font-size: 0.75rem; color: #555; letter-spacing: 0.8px; margin-top: 0.4rem; text-transform: uppercase; }

.about-box {
    background: #111; border: 1px solid #1e1e1e;
    border-left: 3px solid #c9a96e; border-radius: 10px;
    padding: 1rem 1.4rem; margin-bottom: 1.5rem;
    font-size: 0.86rem; color: #888; line-height: 1.7;
}
.about-box b { color: #b8a88a; }

.step-label {
    display: inline-block; background: #161616;
    border: 1px solid #2a2a2a; border-radius: 20px;
    padding: 0.2rem 0.9rem; font-size: 0.75rem;
    color: #c9a96e; letter-spacing: 1px;
    text-transform: uppercase; margin-bottom: 0.5rem;
}
.file-pill {
    display: inline-block; background: #161616;
    border: 1px solid #2a2a2a; border-radius: 8px;
    padding: 0.25rem 0.7rem; font-size: 0.8rem;
    color: #c9a96e; margin: 0.2rem 0.2rem 0.2rem 0;
}
.output-box {
    background: #111; border: 1px solid #2a2a2a;
    border-radius: 12px; padding: 1.4rem 1.6rem;
    margin-top: 0.8rem; line-height: 1.7;
    color: #d4c9b8; font-size: 0.92rem;
    white-space: pre-wrap; max-height: 400px; overflow-y: auto;
}

[data-testid="stFileUploader"] { border: 1.5px dashed #2a2a2a; border-radius: 12px; padding: 0.8rem; background: #111; }
[data-testid="stFileUploader"]:hover { border-color: #c9a96e; }

.stButton > button {
    background: #c9a96e !important; color: #0a0a0a !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important;
    border: none !important; border-radius: 8px !important;
    padding: 0.55rem 1.5rem !important; font-size: 0.92rem !important;
    transition: opacity 0.2s !important; width: 100%;
}
.stButton > button:hover { opacity: 0.85 !important; }

.stSelectbox > div > div { background: #111 !important; border: 1px solid #2a2a2a !important; color: #e8e0d4 !important; border-radius: 8px !important; }
.stTextInput > div > div > input { background: #111 !important; border: 1px solid #2a2a2a !important; color: #e8e0d4 !important; border-radius: 8px !important; }
.stProgress > div > div { background: #c9a96e !important; }
.stAlert { border-radius: 10px !important; border-left: 3px solid #c9a96e !important; background: #111 !important; color: #e8e0d4 !important; }
.stTabs [data-baseweb="tab-list"] { background: #111; border-radius: 10px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { background: transparent; color: #666; border-radius: 8px; font-size: 0.88rem; padding: 0.4rem 1.2rem; }
.stTabs [aria-selected="true"] { background: #c9a96e !important; color: #0a0a0a !important; font-weight: 500; }
hr { border-color: #1e1e1e !important; margin: 1.5rem 0 !important; }
[data-testid="stDownloadButton"] > button { background: #161616 !important; color: #c9a96e !important; border: 1px solid #c9a96e !important; border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important; width: 100%; }
[data-testid="stDownloadButton"] > button:hover { background: #c9a96e !important; color: #0a0a0a !important; }
.stCheckbox > label { color: #888 !important; font-size: 0.86rem !important; }
[data-testid="stSidebar"] { background: #0d0d0d !important; }
.stMultiSelect > div > div { background: #111 !important; border: 1px solid #2a2a2a !important; color: #e8e0d4 !important; border-radius: 8px !important; }

/* Bio sidebar */
.bio-avatar { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid #c9a96e; margin-bottom: 0.5rem; display: block; }
.bio-avatar-placeholder { width: 80px; height: 80px; border-radius: 50%; background: #1e1e1e; border: 2px solid #c9a96e; display: flex; align-items: center; justify-content: center; font-family: 'Cormorant Garamond', serif; font-size: 1.4rem; color: #c9a96e; margin-bottom: 0.5rem; }
.bio-name-small { font-family: 'Cormorant Garamond', serif; font-size: 1.05rem; font-weight: 600; color: #e8e0d4; margin: 0; }
.bio-role-small { font-size: 0.72rem; color: #c9a96e; letter-spacing: 0.4px; text-transform: uppercase; margin-bottom: 0.6rem; }
.bio-link a { font-size: 0.8rem; color: #c9a96e; text-decoration: none; border-bottom: 1px dashed #c9a96e; }
.bio-divider { border: none; border-top: 1px solid #1e1e1e; margin: 0.8rem 0; }

/* Rename sidebar "app" label to "Home" on ALL pages */
[data-testid="stSidebarNav"] ul li:first-child a p {
    font-size: 0 !important;
}
[data-testid="stSidebarNav"] ul li:first-child a p::before {
    content: "Home";
    font-size: 0.875rem !important;
    color: #e8e0d4;
}
</style>
"""

