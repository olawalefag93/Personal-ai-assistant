# Personal AI Assistant

A local AI assistant built with FastAPI, OpenAI, ChromaDB, SQLite memory, tool calling, and a simple web UI.

This project is designed as a practical foundation for a private assistant that can answer questions, use local notes through retrieval-augmented generation, remember recent conversation context by session, and call backend tools.

## What It Does

- Runs a FastAPI backend with a browser-based chat UI
- Uses OpenAI chat models for assistant responses
- Stores per-session chat history in SQLite
- Uses ChromaDB for local vector search over notes
- Supports tool calling through Python functions
- Includes built-in tools for system information and log analysis
- Keeps local notes, databases, logs, and API keys out of Git

## Tech Stack

- Python
- FastAPI
- OpenAI API
- ChromaDB
- SQLite
- HTML, CSS, and JavaScript
- python-dotenv

## Project Structure

```text
personal-ai-assistant/
|-- app/
|   |-- main.py              # FastAPI app, routes, chat endpoint
|   |-- llm_client.py        # OpenAI chat + tool-calling wrapper
|   |-- memory/              # SQLite conversation memory
|   |-- rag/                 # Embeddings and ChromaDB access
|   `-- tools/               # Python tools exposed to the assistant
|-- scripts/
|   `-- ingest_all.py        # Ingest local notes into ChromaDB
|-- web/
|   |-- frontend/index.html  # Browser chat UI
|   `-- static/              # Static assets
|-- .env.example
|-- .gitignore
|-- requirements.txt
`-- README.md
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/olawalefag93/Personal-ai-assistant.git
cd Personal-ai-assistant
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
```

The default local paths are:

```env
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
DB_PATH=./data/assistant.db
VECTOR_DB_PATH=./data/vector_store
KNOWLEDGE_BASE_DIR=./knowledge_base/notes
```

### 5. Add local notes for RAG

Create a local notes directory:

```bash
mkdir -p knowledge_base/notes
```

Add `.md` or `.txt` files to that directory, then ingest them:

```bash
python scripts/ingest_all.py
```

### 6. Start the app

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

## API Examples

Chat endpoint:

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Summarize what this assistant can do.",
    "mode": "default",
    "session_id": "demo"
  }'
```

System information tool endpoint:

```text
http://127.0.0.1:8000/tools/system-info
```

## Assistant Modes

The chat endpoint accepts an optional `mode` value:

- `default` - general personal assistant behavior
- `security` - SOC, logs, incident response, and cybersecurity workflows
- `founder` - business, product, and operations guidance
- `creator` - content ideas, hooks, scripts, and concise explanations

## Tool Calling

The assistant can call backend tools through OpenAI function calling.

Included tools:

- `get_system_info()` - returns basic host system information
- `analyze_log_file(path, max_lines, keyword)` - reads and summarizes log content

New tools can be added by:

1. Creating a Python function in `app/tools/`
2. Adding the function schema to `TOOLS_SPEC` in `app/llm_client.py`
3. Registering the function in `TOOLS_REGISTRY`

## How RAG Works

1. Add Markdown or text files to `knowledge_base/notes`.
2. Run `python scripts/ingest_all.py`.
3. The script chunks the files and stores embeddings in ChromaDB.
4. User questions are embedded and matched against the local vector store.
5. Relevant chunks are passed into the assistant context.

## Local Data And Privacy

The following stay local and are ignored by Git:

- `.env`
- SQLite databases
- ChromaDB vector store files
- Logs
- Private notes under `knowledge_base/notes`

## Roadmap

- Add Docker support
- Add automated tests
- Add chat history browsing in the UI
- Add authentication for the web UI
- Add long-term memory summarization
- Add Wazuh, Docker, and n8n automation tools
- Add optional local model support through Ollama

## License

MIT
