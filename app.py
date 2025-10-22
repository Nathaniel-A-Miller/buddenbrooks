import streamlit as st
import json
import re
import pandas as pd
from pathlib import Path

# ======= CONFIGURATION =======
TEXT_PATH = Path("text/buddenbrooks_ch1.txt")
VOCAB_PATH = Path("vocab/vocab_ch1.json")

# ======= LOAD DATA =======
# Read full text
with open(TEXT_PATH, "r", encoding="utf-8") as f:
    text = f.read()

# Load vocab list (list of dicts)
with open(VOCAB_PATH, "r", encoding="utf-8") as f:
    vocab_list = json.load(f)

# Convert vocab JSON to lookup dict
vocab_dict = {v["word"]: v for v in vocab_list}

# ======= SESSION STATE =======
if "saved" not in st.session_state:
    st.session_state.saved = []

# ======= APP TITLE =======
st.title("📚 Buddenbrooks Vocabulary Trainer")

st.caption("Click on any word you want to memorize. Words you’ve clicked will appear below with definitions and context.")

# ======= TOKENIZE TEXT =======
# Simple tokenization (keep punctuation as separate tokens)
tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

# ======= DISPLAY TEXT WITH CLICKABLE WORDS =======
st.subheader("📖 Text")

cols = st.columns(8)  # layout: 8 words per row
col_index = 0

for token in tokens[:400]:  # limit to first ~400 tokens for speed
    # clean lowercase key
    lookup = token.strip('.,;:"!?()[]').lower()

    # create a button per token
    if cols[col_index].button(token):
        if lookup in vocab_dict and lookup not in st.session_state.saved:
            st.session_state.saved.append(lookup)
    col_index = (col_index + 1) % 8

st.divider()

# ======= SHOW SAVED VOCAB =======
st.subheader("📝 Words to Memorize")

if st.session_state.saved:
    rows = []
    for word in st.session_state.saved:
        entry = vocab_dict.get(word, None)
        if entry:
            rows.append([
                word,
                entry.get("definition_german", ""),
                entry.get("definition_english", ""),
                entry.get("context_snippet", ""),
                entry.get("chapter", "")
            ])
    df = pd.DataFrame(rows, columns=["Word", "German", "English", "Context", "Chapter"])
    st.dataframe(df, use_container_width=True)

    if st.button("Clear Saved Words"):
        st.session_state.saved = []
else:
    st.info("No words selected yet. Click on any word in the text above to start building your list.")

