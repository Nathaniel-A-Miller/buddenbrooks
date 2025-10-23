from pathlib import Path
import json

def load_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")

def load_vocab(path: str) -> dict:
    vocab_list = json.loads(Path(path).read_text(encoding="utf-8"))
    return {v["word"].lower(): v for v in vocab_list}
