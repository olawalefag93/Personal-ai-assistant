import os
import json
from typing import List, Dict, Optional
from app.tools.log_tools import analyze_log_file

from dotenv import load_dotenv
from openai import OpenAI

from app.tools.system_tools import get_system_info

load_dotenv()

client = OpenAI(api_key=os.getenv("open_ai_key"))
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Tool specification for OpenAI function-calling
TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Get basic system information about the machine where OlawaleAI is running.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_log_file",
            "description": "Read and summarize a log file (e.g., /var/log/auth.log). Can optionally filter by a keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Full path to the log file, e.g. /var/log/auth.log",
                    },
                    "max_lines": {
                        "type": "integer",
                        "description": "Maximum number of lines to read from the end of the file (default 500).",
                        "minimum": 50,
                        "maximum": 5000,
                    },
                    "keyword": {
                        "type": "string",
                        "description": "Optional keyword to filter lines (case-insensitive).",
                    },
                },
                "required": ["path"],
            },
        },
    },
]
# Local registry mapping tool names → Python functions
TOOLS_REGISTRY = {
    "get_system_info": get_system_info,
    "analyze_log_file": analyze_log_file,

}


def _build_messages(
    user_message: str,
    system_prompt: Optional[str],
    history: Optional[List[Dict[str, str]]],
    context: Optional[str],
) -> List[Dict[str, str]]:
    messages: List[Dict[str, str]] = []

    combined_system = system_prompt or ""
    if context:
        combined_system += (
            "\n\nYou also have the following context from the user's notes:\n"
            f"{context}\n\nUse it only if it is relevant."
        )

    if combined_system.strip():
        messages.append({"role": "system", "content": combined_system})

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": user_message})

    return messages




def generate_reply(
    user_message: str,
    system_prompt: Optional[str] = None,
    history: Optional[List[Dict[str, str]]] = None,
    context: Optional[str] = None,
    model: Optional[str] = None,
    tools_enabled: bool = False,
) -> str:
    """
    Main wrapper to talk to the LLM.

    If tools_enabled=False:
        - Just call the model normally.

    If tools_enabled=True:
        - First ask the model with tools available.
        - If it requests a tool_call (e.g. get_system_info),
          run the Python function.
        - Then call the model again with the tool result(s)
          as additional messages.
    """

    chosen_model = model or DEFAULT_MODEL
    base_messages = _build_messages(user_message, system_prompt, history, context)

    # --- No tools path: simple call ---
    if not tools_enabled:
        response = client.chat.completions.create(
            model=chosen_model,
            messages=base_messages,
        )
        return response.choices[0].message.content

    # --- Tools-enabled path ---

    # First call: allow the model to decide whether to call any tools.
    first = client.chat.completions.create(
        model=chosen_model,
        messages=base_messages,
        tools=TOOLS_SPEC,
        tool_choice="auto",
    )

    assistant_msg = first.choices[0].message

    # If the model didn't ask for a tool, just return its answer.
    if not getattr(assistant_msg, "tool_calls", None):
        return assistant_msg.content or ""

    # Execute each requested tool.
    tool_messages: List[Dict[str, str]] = []

    for tool_call in assistant_msg.tool_calls:
        func_name = tool_call.function.name
        raw_args = tool_call.function.arguments or "{}"

        try:
            args = json.loads(raw_args)
        except json.JSONDecodeError:
            args = {}

        tool_func = TOOLS_REGISTRY.get(func_name)
        if not tool_func:
            # Unknown tool; skip gracefully
            continue

        # Our current tool (get_system_info) takes no args, but the pattern supports args.
        result = tool_func(**args) if args else tool_func()

        tool_messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": func_name,
                "content": json.dumps(result),
            }
        )

    # Build an assistant message that *includes* tool_calls,
    # as required by the OpenAI API.
    assistant_with_tool_calls = {
        "role": "assistant",
        "content": assistant_msg.content,
        "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in assistant_msg.tool_calls
        ],
    }

    # Second call: original messages + assistant tool_call message + tool outputs.
    messages_with_tools: List[Dict[str, Any]] = []
    messages_with_tools.extend(base_messages)
    messages_with_tools.append(assistant_with_tool_calls)
    messages_with_tools.extend(tool_messages)

    second = client.chat.completions.create(
        model=chosen_model,
        messages=messages_with_tools,
    )

    return second.choices[0].message.content
