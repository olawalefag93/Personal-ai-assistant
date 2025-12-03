# 🤖 Personal AI Assistant — Local RAG + Memory + Tools + Web UI

A fully local, extensible **personal AI assistant** built with:

- **FastAPI** backend  
- **Retrieval-Augmented Generation (RAG)** using ChromaDB  
- **Per-session conversation memory** powered by SQLite  
- **Tool calling** (system info, log analysis, extendable)  
- **Custom web UI**  
- **Environment-based API key loading**  
- **Everything stored locally** for privacy  

This project is designed so *anyone* can use it as a foundation to build their own AI assistant, automate tasks, enhance learning, or explore AI engineering concepts.

---

## 🚀 Features

### 🧠 Smart LLM Agent
- Uses OpenAI models (via API) for reasoning and conversation.
- Configurable “modes” (Security / Founder / Creator)
- Supports multi-step reasoning + function calling for tools.

### 📚 Retrieval-Augmented Generation (RAG)
- Stores your personal notes locally.
- Retrieves relevant information using embeddings.
- Enhances answers with your private knowledge base.
- All data is stored locally for privacy.

### 💬 Conversation Memory (per session)
- Stores chat history in SQLite.
- AI remembers previous messages *within the same session*.
- Does not store anything in the cloud.

### 🧰 Tool Calling (Extensible)
Built-in tools:
- `get_system_info()` — machine information  
- `analyze_log_file(path, max_lines, keyword)` — log inspection  

Easily add your own tools:
- Wazuh log reader  
- Docker container monitor  
- n8n workflow trigger  
- File searcher  
- Anything you want  

### 🖥️ Custom Web UI
- Clean & simple frontend
- Session selector
- Mode selector
- Real-time interactions with your local AI

### 🔐 Private by design
- No logs sent to the cloud  
- No notes uploaded anywhere  
- API keys stored in `.env` only  
- Vector database and memory stored on your device  

---

## 🗂️ Project Structure


personal-ai-assistant/
│
├── app/
│ ├── main.py # FastAPI server, endpoints
│ ├── llm_client.py # OpenAI client + tool logic
│ ├── memory/ # SQLite memory system
│ ├── rag/ # Embeddings + vector database
│ ├── tools/ # Python tool functions
│ └── models.py # Request/response models
│
├── scripts/
│ └── ingest_all.py # RAG ingestion pipeline
│
├── web/
│ └── frontend/
│ └── index.html # Web UI
│
├── data/ # SQLite DB + ChromaDB (ignored)
├── knowledge_base/ # Notes for RAG (ignored)
│
├── .gitignore
├── README.md
├── requirements.txt
└── .env.example


---

## 🛠️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/personal-ai-assistant.git
cd personal-ai-assistant

2. Create & activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Create your .env file
cp .env.example .env
Open it:
   nano .env
Add your OpenAI API key:
   OPENAI_API_KEY=sk-xxxx
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
VECTOR_DB_PATH=./data/vector_store
DB_PATH=./data/assistant.db
5. Ingest your notes (optional but powerful)
Add .md or .txt files to:
knowledge_base/notes/
Run ingestion:

python scripts/ingest_all.py

6. Start the server
uvicorn app.main:app --reload

7. Open the Web UI

Visit:

http://127.0.0.1:8000

You're now chatting with your personal AI assistant!

🔧 Adding Your Own Tools

Tools allow your AI to act, not just talk.
Example tool (in app/tools/my_tool.py):

def say_hello(name: str):
    return {"message": f"Hello, {name}!"}


Register it in TOOLS_SPEC and TOOLS_REGISTRY inside llm_client.py.

The LLM will automatically call this tool when needed.

📚 How RAG Works

Your notes → chunked → embedded → stored in ChromaDB.

When you ask a question:

Your query is embedded

Vector search retrieves the most relevant chunks

Chunks are added to the LLM context

The AI answers using your own knowledge.

RAG = Your personal memory layer.

💾 How Memory Works

Each chat session gets a session_id

Messages are written to a SQLite database

Only messages for the current session are loaded

AI can recall earlier messages in that session

No messages leave your machine

Memory = Short-term, session-based recall.

🧱 Requirements

Python 3.10+

OpenAI API key

Basic command-line familiarity

🛡️ Security

This project includes safeguards:

✔ API keys stored only in .env
✔ .env, SQLite DBs, ChromaDB, logs, notes ignored in git
✔ No personal data ever uploaded
✔ GitHub push-protection friendly

🧭 Roadmap (great for contributors)

Add Docker monitoring tool

Add Wazuh alerts tool

Add n8n integration (trigger workflows)

Add local model support (Ollama)

Add long-term memory summarization

Add authentication for the Web UI

Add chat history browser in UI

🤝 Contributing

Fork the repo and open a pull request.
Feel free to extend tools, RAG, UI, memory, or backend logic.

📄 License

MIT License.
Feel free to reuse, modify, and build upon this project.

⭐ Acknowledgements

This project was built for learning and exploration in:

AI engineering

RAG systems

Tool calling

Backend architecture

Cybersecurity automation

Personal assistants

If you build something cool on top of this — share it!



