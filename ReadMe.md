# 🤖 AutoResearcher

> An autonomous AI research platform that thinks, searches, debates, and reports — so you don't have to.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-green)
![Tavily](https://img.shields.io/badge/Tavily-Search-orange)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## What is AutoResearcher?

Most AI tools answer one question at a time. AutoResearcher is different — it runs **autonomous multi-agent pipelines** that search the web, reason over real data, debate each other, and produce structured professional reports from a single input.

Three tools. One platform. Zero GPU required.

---

## 🛠️ Tools

### 🕵️ Conspiracy Debunker
Type any conspiracy theory. Three AI agents kick in automatically:
- A **Search Agent** pulls real web sources
- A **Pro Agent** builds the strongest case FOR the conspiracy
- A **Con Agent** builds the strongest case AGAINST it
- A **Judge Agent** reads both, spots logical fallacies, and delivers a verdict with a confidence score

If confidence is too low, the system **autonomously generates new search strategies and loops** until it's sure.

---

### 🎬 Movie DNA Analyzer
Type a genre or vibe (e.g. *"dark psychological thrillers"*). The system:
- Finds the 6 most iconic hit shows in that genre
- Researches what made each one work
- Extracts the **hidden DNA** — patterns they all share
- Writes a **full original show pitch** using that formula
- Scores any existing show against the DNA formula

---

### 🚀 Startup Idea Evaluator
Describe a startup idea in plain English. The system:
- Researches **market size, growth rate, and trends**
- Hunts down **real existing competitors**
- Scores the idea across **5 VC dimensions** with a GO / NO-GO decision
- Writes a full **investor memo** — the kind a VC reads before taking a meeting

---

## 🏗️ Architecture

```
autoResearcher/
├── app.py                              ← Home landing page
├── agents.py                           ← Conspiracy Debunker agents
├── movie_agents.py                     ← Movie DNA Analyzer agents
├── startup_agents.py                   ← Startup Evaluator agents
├── pages/
│   ├── 1_🕵️_Conspiracy_Debunker.py   ← Conspiracy UI
│   ├── 2_🎬_Movie_DNA_Analyzer.py     ← Movie DNA UI
│   └── 3_🚀_Startup_Evaluator.py      ← Startup Evaluator UI
├── .env                                ← API keys (never commit this)
└── requirements.txt                    ← Dependencies
```

### Agent count

| Tool | Agents |
|---|---|
| Conspiracy Debunker | 5 |
| Movie DNA Analyzer | 5 |
| Startup Evaluator | 4 |
| **Total** | **14** |

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Language model | OpenAI GPT-4o |
| Web search | Tavily API |
| UI | Streamlit |
| Secret management | python-dotenv |
| Language | Python 3.10+ |

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/autoResearcher.git
cd autoResearcher
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API keys

Create a `.env` file in the root folder:

```
OPENAI_KEY=sk-...
TAVILY_KEY=tvly-...
```

Get your keys here:
- OpenAI → [platform.openai.com](https://platform.openai.com)
- Tavily → [tavily.com](https://tavily.com) *(1000 free searches/month)*

### 5. Run the app

```bash
streamlit run app.py
```

App opens at `http://localhost:8501`

---

## 💡 How It Works

### The AutoResearch Loop (Conspiracy Debunker)

```
Claim → Search → Pro Agent → Con Agent → Judge → Confident? 
                                                      ↓ NO
                                            Generate new queries
                                                      ↓
                                                   Repeat
                                                      ↓ YES
                                               Final Verdict
```

### The DNA Pipeline (Movie Analyzer)

```
Genre → Find Shows → Research Each → Extract DNA → Pitch → Score
```

### The Evaluation Pipeline (Startup Evaluator)

```
Idea → Market Research ──→ Scorer → Investor Memo
     → Competitor Research ──↑
```

---

## 🧠 Key Concepts Used

| Concept | Where it's used |
|---|---|
| RAG (Retrieval Augmented Generation) | All three tools — real web search fed into GPT |
| Multi-agent systems | All three tools — specialized agents with different roles |
| Structured output prompting | All agents — strict format parsing into Python dicts |
| Agent chaining | Movie DNA + Startup Evaluator — output of one feeds next |
| Autonomous loops | Conspiracy Debunker — loops until confident enough |
| Callback pattern | All tools — live status updates streamed to UI |
| Multipage Streamlit | App structure — pages/ folder auto-creates sidebar nav |

---

## 📦 Requirements

```
openai
tavily-python
streamlit
python-dotenv
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## ⚠️ Important Notes

- **Never commit your `.env` file** — add it to `.gitignore`
- **No GPU required** — everything runs on API calls
- **Costs** — each full run uses ~10–20 API calls. Estimated cost per run: ~$0.05–0.10 with GPT-4o
- **Rate limits** — Tavily free tier gives 1000 searches/month. Each run uses ~6–10 searches

---

## 🔒 .gitignore

Make sure your `.gitignore` includes:

```
.env
venv/
__pycache__/
*.pyc
.DS_Store
```

---

## 🏆 Built at a Hackathon

AutoResearcher was built as a hackathon project exploring the AutoResearcher pattern — autonomous AI agents that plan, search, reason, and iterate without human intervention between steps.

---

## 📄 License

MIT License — free to use, modify, and build on.

---

*Built with ❤️ using OpenAI · Tavily · Streamlit*