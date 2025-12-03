from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from app.rag.vector_store import query_documents
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.tools.system_tools import get_system_info


from app.memory.models import init_db, get_or_create_conversation, add_message, get_recent_messages

from app.llm_client import generate_reply

load_dotenv()

app = FastAPI(title="OlawaleAI")

@app.on_event("startup")
def on_startup():
    # Ensure the SQLite DB and tables exist
    init_db()


BASE_DIR = Path(__file__).resolve().parent.parent

# Optional: if you later add CSS/JS files in web/static
app.mount("/static", StaticFiles(directory=BASE_DIR / "web" / "static"), name="static")


@app.get("/", response_class=FileResponse)
def serve_frontend():
    """
    Serve the main web UI.
    """
    index_path = BASE_DIR / "web" / "frontend" / "index.html"
    return FileResponse(index_path)




class ChatRequest(BaseModel):
    message: str
    mode: str | None = None          # "security", "founder", "creator", or None
    session_id: str | None = None    # conversation identifier



class ChatResponse(BaseModel):
    reply: str
    session_id: str

BASE_SYSTEM_PROMPT = """
You are OlawaleAI, a helpful personal AI assistant for Olawale.
You explain things clearly, step-by-step, and relate topics to:
- cybersecurity and homelab work,
- automation and scripting,
- building projects and businesses like JollofSpace.

If you don't know something, say so honestly and suggest next steps.
"""
SECURITY_MODE_PROMPT = """
You are OlawaleAI in SECURITY ANALYST mode.

Focus on:
- SOC workflows, alert triage, incident response.
- Wazuh, Suricata, Snort, SIEM, log analysis.
- Explaining security concepts clearly and practically.
Use real-world, hands-on language.
"""

FOUNDER_MODE_PROMPT = """
You are OlawaleAI in FOUNDER / BUSINESS mode.

Focus on:
- JollofSpace and similar marketplace ideas.
- Pricing, unit economics, vendor onboarding, operations.
- Practical steps for small, bootstrapped businesses.
Speak like a smart but down-to-earth advisor.
"""

CREATOR_MODE_PROMPT = """
You are OlawaleAI in CREATOR / CONTENT mode.

Focus on:
- Social media ideas, hooks, captions, scripts.
- Explaining complex topics simply for TikTok/Twitter/IG.
- Keeping tone engaging, clear, and scroll-stopping.
"""


def get_system_prompt_for_mode(mode: str | None) -> str:
    """
    Return the appropriate system prompt based on the requested mode.
    """
    if mode == "security":
        return BASE_SYSTEM_PROMPT + "\n\n" + SECURITY_MODE_PROMPT
    elif mode == "founder":
        return BASE_SYSTEM_PROMPT + "\n\n" + FOUNDER_MODE_PROMPT
    elif mode == "creator":
        return BASE_SYSTEM_PROMPT + "\n\n" + CREATOR_MODE_PROMPT
    else:
        # default mode
        return BASE_SYSTEM_PROMPT

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    """
    Main chat endpoint with:
    - modes (security/founder/creator/default)
    - conversation memory (per session_id)
    - basic RAG over notes
    """
    user_message = payload.message
    mode = payload.mode or "default"

    # Use provided session_id or default
    session_id = payload.session_id or "default"

    # 1) Get or create conversation row
    conversation_id = get_or_create_conversation(session_id)

    # 2) Load recent history for this conversation
    history = get_recent_messages(conversation_id, limit=10)

    # 3) RAG: query your notes
    retrieved = query_documents(
        collection_name="knowledge",
        query_text=user_message,
        n_results=4,
    )

    context_parts = []
    for item in retrieved:
        source = item["metadata"].get("source", "unknown")
        chunk_index = item["metadata"].get("chunk_index", 0)
        text = item["text"]
        context_parts.append(
            f"[Source: {source} | Chunk: {chunk_index}]\n{text}"
        )

    context_text = "\n\n---\n\n".join(context_parts) if context_parts else ""

    # 4) Choose appropriate system prompt for mode
    system_prompt = get_system_prompt_for_mode(mode)

    # 5) Call LLM with system prompt + history + RAG context
    ai_reply = generate_reply(
        user_message=user_message,
        system_prompt=system_prompt,
        history=history,
        context=context_text,
        tools_enabled=True,      # < - - allow the model to call tools
    )

    # 6) Save new messages into DB (user + assistant)
    add_message(conversation_id, "user", user_message)
    add_message(conversation_id, "assistant", ai_reply)

    # 7) Return reply + session_id (so client can reuse it)
    return ChatResponse(reply=ai_reply, session_id=session_id)


@app.get("/tools/system-info")
def tool_system_info():
    """
    Simple HTTP endpoint to see a backend 'tool' in action.
    This is NOT yet wired into the LLM, but it's the first step.
    """
    return get_system_info()
