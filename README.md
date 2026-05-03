# 🔍 Web Research Agent

An AI-powered research agent that autonomously searches the web and compiles structured intelligence briefings on any topic.

Built with **Python + FastAPI** (backend) and **React** (frontend), powered by the **Anthropic Claude API** with real-time web search.

---

## ✨ Features

- **Agentic web search** — Claude autonomously performs multiple targeted searches
- **Structured reports** — Executive summary, key findings, analysis, conclusion, and sources
- **Real-time data** — Always up-to-date via live web search
- **Clean UI** — Dark, professional frontend built with React (no build step needed)
- **REST API** — Easily extendable FastAPI backend with Swagger docs at `/docs`

---

## 🗂 Project Structure

```
web-research-agent/
├── main.py              # FastAPI app — routes & server
├── agent.py             # Research agent — Claude + web search logic
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── static/
    └── index.html       # React frontend (CDN-based, no build step)
```

---

## 🚀 Setup & Run

### 1. Clone or download the project

```bash
git clone https://github.com/yourusername/web-research-agent
cd web-research-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your Anthropic API key

```bash
cp .env.example .env
# Edit .env and add your key:
# ANTHROPIC_API_KEY=sk-ant-...
```

Get your API key at: https://console.anthropic.com

### 5. Run the server

```bash
python main.py
```

Open your browser at: **http://localhost:8000**

API docs available at: **http://localhost:8000/docs**

---

## 🧠 How It Works

```
User enters topic
      ↓
FastAPI receives POST /api/research
      ↓
agent.py sends request to Claude claude-sonnet-4-20250514
with web_search_20250305 tool enabled
      ↓
Claude autonomously:
  1. Decides what to search
  2. Executes multiple web searches
  3. Reads and cross-references results
  4. Synthesizes a structured JSON briefing
      ↓
FastAPI returns structured report
      ↓
React renders report with sections:
  Executive Summary / Key Findings /
  Analysis / Conclusion / Sources
```

---

## 📡 API Reference

### `POST /api/research`

**Request body:**
```json
{
  "topic": "Your research topic here"
}
```

**Response:**
```json
{
  "executive_summary": "High-level overview...",
  "key_findings": [
    { "title": "Finding title", "detail": "Detailed explanation..." }
  ],
  "analysis": "Deeper analysis paragraph...",
  "conclusion": "Forward-looking conclusion...",
  "sources": [
    { "title": "Source title", "url": "https://..." }
  ],
  "search_queries": ["query 1", "query 2"]
}
```

---

## 🛠 Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | Python 3.10+, FastAPI, Uvicorn      |
| AI        | Anthropic Claude claude-sonnet-4-20250514          |
| Search    | Claude web_search_20250305 tool     |
| Frontend  | React 18 (CDN), Vanilla CSS         |
| Fonts     | Syne, DM Sans, JetBrains Mono       |

---

## 🔮 Possible Extensions

- Add streaming with Server-Sent Events for live output
- Save reports to a database (SQLite / PostgreSQL)
- Export reports as PDF
- Add topic history and saved briefings
- Deploy to Railway, Render, or AWS

---

## 📄 License

MIT
