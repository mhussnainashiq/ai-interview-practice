import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path(__file__).resolve().parent.parent / "interview_history.json"

def load_history():
    try:
        if HISTORY_FILE.exists():
            data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []
    return []

def save_session(session):
    history = load_history()
    safe_session = dict(session)
    safe_session["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    history.append(safe_session)
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")

def clear_history():
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()
