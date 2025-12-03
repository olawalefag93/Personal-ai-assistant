import platform
import os
from pathlib import Path


def get_system_info() -> dict:
    """
    Simple example tool that returns basic system info.
    Lives on the backend. Later, the LLM can call this.
    """
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cwd": os.getcwd(),
        "project_root": str(Path(__file__).resolve().parent.parent.parent),
        "storage_notes": "Main AI project is on /mnt/external-ssd",
    }
