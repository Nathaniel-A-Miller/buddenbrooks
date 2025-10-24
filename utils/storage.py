from tinydb import TinyDB, Query
from pathlib import Path

DB_PATH = Path("data/user_data.json")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
db = TinyDB(DB_PATH)
User = Query()

def load_saved_words(username="default_user"):
    """Return a Python set of saved words for a given user."""
    record = db.get(User.name == username)
    if record:
        return set(record.get("saved_words", []))
    return set()

def save_saved_words(saved_words, username="default_user"):
    """Write the saved words to disk."""
    db.upsert({"name": username, "saved_words": list(saved_words)}, User.name == username)
