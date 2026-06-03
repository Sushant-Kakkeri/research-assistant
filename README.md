# 🔬 MCP Research Assistant

> **An autonomous AI research agent powered by MCP (Model Context Protocol) — MCP decides which tools to use, in what order, automatically.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Cloud-FF4B4B?logo=streamlit)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?logo=openai)](https://openai.com)
[![LangChain](https://img.shields.io/badge/LangChain-FAISS-1C3C3C)](https://langchain.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**Live Demo:** [research-assistant on Streamlit Cloud](https://github.com/Sushant-Kakkeri/research-assistant)

---

## 🧠 What Makes This Different

Most AI assistants use a **router** — a hardcoded system that looks at keywords and sends the question to either a document search or a web search. This app works fundamentally differently.

**MCP (Model Context Protocol) is an autonomous agent loop.** When you ask a question, MCP doesn't just pick one tool and answer. It:

1. Reads the question and plans a research strategy
2. Calls the most relevant tool (e.g., Wikipedia for background)
3. Reads the result, then decides — do I have enough? Or do I need more?
4. Calls the next tool (e.g., web search for current data)
5. Repeats until it has comprehensive information
6. Writes a final synthesized answer, optionally generating and saving a report

**No router. No hardcoded logic. MCP decides everything.**

```
Traditional Router App:         MCP Agent App:
──────────────────────          ──────────────────────────────
User → Router → RAG             User → MCP thinks...
            ↘ Web                     → calls Wikipedia
            → Answer                  → reads result
                                      → calls web_search
                                      → reads result
                                      → calls search_documents
                                      → reads result
                                      → generates report
                                      → saves to file
                                      → Final answer
```

---

## ✨ Key Features

- **🤖 Autonomous MCP Agent Loop** — iterates up to 10 tool calls per question until it has sufficient information
- **📄 RAG as an MCP Tool** — document search is just another tool in the agent's toolbox, called automatically when PDFs are uploaded
- **🌐 Multi-Source Research** — combines Wikipedia background knowledge, live web search, and breaking news in a single response
- **📊 Report Generation** — compiles all findings into a structured, timestamped research report
- **💾 Report Saving** — saves reports to `reports/` directory as `.txt` files, named by topic + timestamp
- **🔍 Transparent Reasoning** — every tool call MCP makes is displayed in the UI with an expandable research steps panel
- **🔄 Conversation Memory** — retains last 3 exchanges for contextual follow-up questions
- **☁️ Streamlit Cloud Deployed** — accessible from any browser with no local setup

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **UI** | Streamlit |
| **AI Model** | OpenAI GPT-4o |
| **Agent Framework** | Custom MCP Agent Loop (OpenAI function calling) |
| **Vector Store** | FAISS (Facebook AI Similarity Search) |
| **Embeddings** | OpenAI `text-embedding-ada-002` |
| **Document Loader** | LangChain + PyPDF |
| **Web Search** | DuckDuckGo Search (with Wikipedia fallback) |
| **News Search** | DuckDuckGo News API |
| **Knowledge Base** | Wikipedia Python API |
| **Deployment** | Streamlit Cloud |

---

## 📁 Project Structure

```
research-assistant/
│
├── app.py              # Streamlit UI — chat interface, tool badges,
│                       # research step display, demo question buttons
│
├── mcp_agent.py        # The MCP Agent brain — the autonomous loop
│                       # that iterates tool calls until research complete
│
├── tools.py            # All 7 tool definitions + execute_tool dispatcher
│                       # web_search, wikipedia_search, news_search,
│                       # search_documents (RAG), generate_report,
│                       # save_report, get_current_datetime
│
├── rag_tool.py         # RAG Engine using FAISS
│                       # PDF ingestion, chunking, similarity search
│
├── requirements.txt    # Python dependencies
├── runtime.txt         # Python version pin (3.11)
└── .gitignore          # Excludes .env, reports/, __pycache__
```

---

## 🤖 The 7 MCP Tools

| Tool | When MCP Uses It | Source |
|---|---|---|
| `web_search` | Current facts, recent events, live data | DuckDuckGo → Wikipedia fallback |
| `wikipedia_search` | Background knowledge, history, definitions | Wikipedia API |
| `news_search` | Breaking news from the past week | DuckDuckGo News |
| `search_documents` | Content from uploaded PDFs | FAISS RAG vector store |
| `generate_report` | After gathering research, to compile findings | In-memory formatter |
| `save_report` | When user wants to keep the report | Local `reports/` directory |
| `get_current_datetime` | Timestamps, date-aware questions | Python `datetime` |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- OpenAI API key — [get one here](https://platform.openai.com/api-keys)

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/Sushant-Kakkeri/research-assistant.git
cd research-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your environment
cp .env.example .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-key-here

# 4. Run the app
streamlit run app.py
```

### Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-openai-key-here
```

---

## 💡 How to Use

### Basic Research
Type any question in the chat input. MCP will automatically decide which tools to use:

```
"Research the latest developments in quantum computing"
→ MCP calls: wikipedia_search → web_search → news_search
→ Synthesizes all three sources into one comprehensive answer
```

### Document-Enhanced Research
Upload a PDF in the sidebar, then ask questions that combine your document with live data:

```
"Research Mars exploration — search my documents AND find latest mission news"
→ MCP calls: search_documents → wikipedia_search → web_search → news_search
→ Combines your private document with live internet research
```

### Full Report Generation
Ask for a comprehensive report and MCP will use all tools, compile findings, and optionally save to file:

```
"Research quantum computing thoroughly and generate a complete report and save it"
→ MCP calls: wikipedia_search → web_search → news_search
            → generate_report → save_report
→ Saves to: reports/quantum_computing_20260601_143022.txt
```

### Demo Questions
Three quick-start buttons are available in the UI:
- 🌍 **Research AI developments** — multi-source web + Wikipedia + news
- 🚀 **Research Mars + my documents** — combines RAG with live search  
- 📊 **Quantum computing full report** — full pipeline including save

---

## 🔍 Transparency — MCP Research Steps

Every response shows which tools were called, displayed as color-coded badges:

| Badge Color | Tool |
|---|---|
| 🟢 Green | `web_search` |
| 🔵 Blue | `wikipedia_search` |
| 🟠 Orange | `news_search` |
| 🟣 Purple | `search_documents` |
| 🔴 Red | `generate_report` |
| 🟤 Brown | `save_report` |
| ⚫ Grey | `get_current_datetime` |

An expandable **🔍 MCP Research Steps** panel shows each tool call and its argument, letting you see exactly how MCP reasoned through the research.

---

## 🔧 Deployment on Streamlit Cloud

1. Push your code to GitHub (ensure `.env` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set `app.py` as the main file
4. Under **Settings → Secrets**, add:

```toml
OPENAI_API_KEY = "sk-your-openai-key-here"
```

5. Deploy — the app will be live at `your-app-name.streamlit.app`

---

## 📊 Comparison: MCP Agent vs Traditional Router

| Capability | Traditional Router | MCP Agent |
|---|---|---|
| Decision maker | Hardcoded keyword rules | GPT-4o reasoning |
| Tools per question | Always exactly 1 | 1 to 10, as needed |
| Can combine sources | Only with explicit BOTH mode | Always, automatically |
| Report generation | ❌ | ✅ |
| Save to file | ❌ | ✅ |
| Adapts to complexity | ❌ | ✅ |
| Visible reasoning steps | ❌ | ✅ |

---

## 🗺️ Related Projects

This app is part of a two-app AI portfolio:

| App | Description | Repo |
|---|---|---|
| **MCP Research Assistant** *(this app)* | Autonomous MCP agent with multi-tool research loop | [research-assistant](https://github.com/Sushant-Kakkeri/research-assistant) |
| **Smart RAG + MCP Demo** | Smart router with LangSmith monitoring + streaming | [rag-mcp-demo](https://github.com/Sushant-Kakkeri/rag-mcp-demo) |

---

## 👨‍💻 Author

**Sushant Kakkeri**
Senior Enterprise Software Engineer

- 15+ years of enterprise BPM and CRM experience
- Pega Lead Certified Architect (LCA Part 1), Senior System Architect (SSA)
- Expanding into Cloud & AI — AWS, LangChain, Streamlit, OpenAI

---

## 📄 License

Copyright © 2026 Sushant Kakkeri. All Rights Reserved.

---

*Built with OpenAI GPT-4o · LangChain · FAISS · Streamlit · DuckDuckGo Search · Wikipedia API*
