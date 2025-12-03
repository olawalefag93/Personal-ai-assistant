import os
from pathlib import Path
from typing import List, Dict, Optional


# You can tune this: only allow logs from these base directories
ALLOWED_LOG_DIRS = [
    Path("/var/log"),
    Path("/mnt/external-ssd/olawale_ai/logs"),  # you can create/use this too
]


def _is_allowed_path(path: Path) -> bool:
    """
    Ensure the requested log path is inside one of the allowed directories.
    Prevents the AI from reading arbitrary system files.
    """
    try:
        path = path.resolve()
    except FileNotFoundError:
        return False

    for base in ALLOWED_LOG_DIRS:
        try:
            base = base.resolve()
        except FileNotFoundError:
            continue
        if base in path.parents or path == base:
            return True
    return False


def analyze_log_file(
    path: str,
    max_lines: int = 500,
    keyword: Optional[str] = None,
) -> Dict:
    """
    Read up to max_lines from the end of a log file and
    optionally filter lines containing a keyword.

    Returns:
    - summary (basic counts)
    - sample_lines (up to ~20 lines)
    """

    log_path = Path(path)

    if not _is_allowed_path(log_path):
        return {
            "error": f"Path '{path}' is not in allowed log directories.",
            "allowed_dirs": [str(p) for p in ALLOWED_LOG_DIRS],
        }

    if not log_path.exists():
        return {"error": f"Log file does not exist: {path}"}

    # Safely read last max_lines from the file
    try:
        with log_path.open("r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
    except Exception as e:
        return {"error": f"Failed to read log file: {e}"}

    total_lines = len(all_lines)
    start_index = max(0, total_lines - max_lines)
    lines = all_lines[start_index:]

    if keyword:
        lines = [ln for ln in lines if keyword.lower() in ln.lower()]

    # Build a simple summary
    summary = {
        "path": str(log_path),
        "total_lines_in_file": total_lines,
        "analyzed_last_lines": min(max_lines, total_lines),
        "filtered_keyword": keyword or "",
        "matched_lines": len(lines),
    }

    # Limit sample lines so we don't flood the model
    sample_lines = lines[-20:]

    return {
        "summary": summary,
        "sample_lines": sample_lines,
    }
