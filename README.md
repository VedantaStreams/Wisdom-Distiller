# 🕉️ Wisdom Distiller

### *Śravaṇa · Manana · Nididhyāsana*

> *Distilling the wisdom of sacred discourses into clear, lasting insights.*

**Wisdom Distiller** is an AI-powered spiritual study companion built exclusively for seekers and students of Vedānta. It transcribes, summarizes, and extracts wisdom from spiritual discourses — preserving Sanskrit in Devanāgarī script, supporting seven Indian languages, and producing beautifully formatted outputs for study, reflection, and archiving.

🌐 **Live App:** [wisdomdistiller.vedantadhara.com](https://wisdomdistiller.vedantadhara.com)

Built with **Streamlit · Anthropic Claude · OpenAI Whisper**

---

## ✨ What Makes This App Unique

- 🕉️ **Built exclusively for Vedantic discourses** — every prompt is tuned for Sanskrit terminology, scriptural references, and the Guru–Śiṣya tradition
- **Sanskrit always in Devanāgarī** — verses are never transliterated into Roman script
- 🌐 **Seven Indian languages** — English, Hindi, Kannada, Telugu, Tamil, Marathi, Gujarati
- 📋 **Six output formats** — tailored for every kind of seeker
- 🪷 **Personal Reflection Journal** — capture your own manana alongside the AI output
- 🎯 **Custom Focus Prompts** — 25 presets to direct the AI's attention to specific themes, cross-references, or analogies
- 📥 **Export to TXT, PDF, DOCX** — with full formatting and Sanskrit fonts preserved
- 🙏 **Offered as seva** — no ads, no data stored, no paywalls

---

## 📄 Pages & Features

| # | Page | Description |
|---|---|---|
| 1 | 🙏 **Reverence & Gratitude** | Dedicated to Pūjya Swāmī Chinmayānandajī, Swāmī Aparājitānandajī & Swāmī Śaraṇānandajī (Chinmaya Mission Chicago) |
| 2 | 🎙️ **Audio Summarizer** | Upload 1–5 MP3/M4A/WAV files → transcribe → summarize in 6 formats |
| 3 | 📜 **Discourse Transcriber** | Full structured transcript with section headings, Sanskrit glossary & custom focus prompts |
| 4 | 🎬 **Video Summarizer** | YouTube URL or MP4 upload → transcript & summary |
| 5 | 📄 **Document Combiner** | Merge multiple transcripts into one unified summary |
| 6 | 💎 **Wisdom Extractor** | Verbatim quotes · YouTube titles · Reel captions · Hashtags |
| 7 | 🕉️ **About the App** | What makes Wisdom Distiller unique |
| 8 | ❓ **FAQ** | Getting started, troubleshooting, API key help |
| 9 | 🪷 **Sādhanā & Seva** | About the creator |
| 10 | 📱 **Get the App** | How to access on iPhone, Android & desktop |

---

## 📁 Project Structure

```
Wisdom-Distiller/
├── app.py                                  ← Home page & navigation
├── pages/
│   ├── 1_Reverence_and_Gratitude.py       ← Pranāms & Gratitude
│   ├── 2_Audio_Summarizer.py              ← Audio transcription & summarization
│   ├── 3_Discourse_Transcriber.py         ← Full structured transcript
│   ├── 4_Video_Summarizer.py              ← Video & YouTube audio
│   ├── 5_Document_Combiner.py             ← Merge transcripts
│   ├── 6_Wisdom_Extractor.py              ← Verbatim quote extraction
│   ├── 7_About_the_App.py                 ← App features & uniqueness
│   ├── 8_FAQ.py                           ← Frequently asked questions
│   ├── 9_Sadhana_and_Seva.py             ← About the creator
│   └── 10_Get_the_App.py                  ← Mobile & sharing guide
├── utils/
│   ├── helpers.py                          ← Transcription, summarization, translation, export
│   ├── styles.py                           ← Shared CSS (dark theme)
│   └── usage_tracker.py                   ← Session-based usage tracking
├── .streamlit/
│   └── config.toml                        ← Dark theme configuration
├── Om.jpeg                                 ← Om symbol
├── Gurudev.jpg                             ← Swāmī Chinmayānandajī photo
├── swami_aparajitananda.jpg               ← Swāmī Aparājitānandajī photo
├── swami_sarananda.jpeg                   ← Swāmī Śaraṇānandajī photo
├── packages.txt                            ← System packages (ffmpeg, fonts-noto)
├── requirements.txt                        ← Python dependencies
└── README.md
```

---

## 🎯 Output Formats (Audio Summarizer)

| Format | Best For |
|---|---|
| **Bullet Highlights** | Quick review, key points at a glance |
| **Main Takeaways** | Essential teachings in brief |
| **Detailed Paragraphs** | Deep reading, full prose summary |
| **Executive Brief** | Concise one-page overview |
| **Academic Digest** | Scholarly format with arguments, evidence & notable quotes |
| **Structured Table** | Main Point · Explanation · Example · Personal Reflection |

---

## 📜 Discourse Transcriber — Special Features

- **Full structured transcript** — every sentence preserved, organized into meaningful sections
- **Auto section headings** — Introduction, Main Teaching, Scriptural Explanation, Story/Analogy, Practical Application
- **Sanskrit Terms Glossary** — auto-generated at the end of every transcript
- **Custom Focus Prompts** — 25 presets organized into 6 categories:
  - 📌 Emphasis & stress — highlight repeated or stressed points
  - 📚 Cross-references — identify other scriptures cited
  - 🎭 Teaching style — flag analogies, stories, rhetorical questions
  - 🕉️ Sanskrit study — mark terms, shlokas with sources
  - 🧠 Specific themes — mind, ego, surrender, Ātman/Brahman, mokṣa
  - 📱 Social sharing — extract quotable statements
- **Search within transcript** — find any term instantly
- **My Reflections** — personal notes included in the download

---

## 🌐 Languages Supported

| Language | Script |
|---|---|
| English | Latin |
| हिन्दी Hindi | Devanāgarī |
| ಕನ್ನಡ Kannada | Kannada script |
| తెలుగు Telugu | Telugu script |
| தமிழ் Tamil | Tamil script |
| मराठी Marathi | Devanāgarī |
| ગુજરાતી Gujarati | Gujarati script |

> **Sanskrit verses always appear in Devanāgarī script** regardless of the output language selected.

---

## 🔑 API Keys Required

| Key | Source | Used For |
|---|---|---|
| **Anthropic API Key** | [console.anthropic.com](https://console.anthropic.com) | Claude — summarization, structuring, translation |
| **OpenAI API Key** | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | Whisper — audio transcription |

Keys are entered on the Home page sidebar. They are **never stored** — they exist only in your current browser session.

---

## 💰 Estimated API Cost Per Session

| Task | Whisper (OpenAI) | Claude (Anthropic) | Total |
|---|---|---|---|
| 20 min audio | ~$0.12 | ~$0.02 | ~$0.14 |
| 1 hour audio | ~$0.36 | ~$0.04 | ~$0.40 |
| 2 hour audio | ~$0.72 | ~$0.06 | ~$0.78 |

*Costs are approximate. Both services offer free credits for new accounts.*

---

## 🖥️ Run Locally

### 1. Install system dependencies
```bash
brew install ffmpeg          # macOS
sudo apt install ffmpeg      # Ubuntu/Debian
winget install ffmpeg        # Windows
```

### 2. Clone the repo
```bash
git clone https://github.com/VedantaStreams/Discourse-summary.git
cd Discourse-summary
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Add API keys — create `.streamlit/secrets.toml`
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
OPENAI_API_KEY    = "sk-..."
```

### 5. Run
```bash
streamlit run app.py
```
Opens at `http://localhost:8501`

---

## ☁️ Deploy on Streamlit Cloud

1. Push all files to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Select repo · set main file to `app.py`
4. Under **Settings → Secrets** add:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
OPENAI_API_KEY    = "sk-..."
UNLIMITED_ACCESS  = "true"
```
5. Deploy

### Custom Domain (Namecheap)
- Namecheap → Advanced DNS → Add **URL Redirect Record**
- Host: `wisdomdistiller` · Value: `https://wisdomdistiller.streamlit.app`
- Share: **wisdomdistiller.vedantadhara.com**

---

## 📦 Dependencies

```
streamlit       — web framework
anthropic       — Claude API
openai          — Whisper API
reportlab       — PDF export (fallback)
weasyprint      — PDF export (primary, with Indian font support)
python-docx     — Word document export
Pillow          — Image processing
fonttools       — Sanskrit/Telugu font rendering
```

System packages (`packages.txt`): `ffmpeg` · `fonts-noto`

---

## 🔧 Troubleshooting

| Error | Fix |
|---|---|
| App shows "Oh no" error | Click ⋮ → **Reboot app** · Re-enter API keys after reboot |
| Transcription garbled | Use MP3/M4A at 128kbps+ · Minimize background noise |
| Sanskrit shows as boxes | Open file with a Unicode font (Noto Sans, Arial Unicode MS) |
| API key not working | Anthropic: starts `sk-ant-` · OpenAI: starts `sk-` · Check for spaces |
| `ffmpeg not found` | Ensure `packages.txt` with `ffmpeg` is in repo root |
| PDF shows only summary | Use **Discourse Transcriber** page for full transcript PDF |
| Pages in wrong order | Files must be prefixed: `1_`, `2_`, `3_` etc. |

---

## 🙏 About

Created by **Suma Rajashankar** — PhD in Physics (IISc Bangalore), Senior Data Scientist / AI Engineer at Capital One, and a sincere student of Vedānta through the Chinmaya Mission.

This app is offered as a small *seva* — with deep gratitude to **Pūjya Swāmī Aparājitānandajī** and **Pūjya Swāmī Śaraṇānandajī** of Chinmaya Mission Chicago, and to **Pūjya Swāmī Chinmayānandajī**, whose eternal light continues to guide all seekers.

*With pranāms* 🙏

---

*Śravaṇa · Manana · Nididhyāsana*
