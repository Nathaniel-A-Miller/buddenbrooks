import streamlit as st
from components.text_viewer_html import render_text_html
from pathlib import Path
import json
from utils.storage import load_saved_words, save_saved_words

st.set_page_config(layout="wide", page_title="Buddenbrooks Reader")

# --- Load text ---
TEXT_PATH = Path("data/text/buddenbrooks_ch1.txt")
VOCAB_PATH = Path("data/vocab/vocab_ch1.json")

text = TEXT_PATH.read_text(encoding="utf-8")
vocab_list = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
vocab_dict = {v["word"].lower(): v for v in vocab_list}

tokens = text.split()  # for pagination if needed

# --- Load saved words ---
if "saved_words" not in st.session_state:
    st.session_state.saved_words = load_saved_words("default_user")

# --- Hidden input to capture clicked words ---
clicked_word = st.text_input("", key="clicked_word", label_visibility="collapsed")
if clicked_word:
    word = clicked_word.lower()
    if word in st.session_state.saved_words:
        st.session_state.saved_words.remove(word)
    else:
        st.session_state.saved_words.add(word)
    st.session_state.clicked_word = ""  # reset for next click

# --- Sidebar ---
st.sidebar.header("📘 Saved Vocabulary")
if st.session_state.saved_words:
    for word in sorted(st.session_state.saved_words):
        st.sidebar.markdown(f"**{word}** — {vocab_dict[word]['definition_english']}")
    if st.sidebar.button("Clear Saved Words"):
        st.session_state.saved_words.clear()
else:
    st.sidebar.info("No words saved yet.")

# --- Render text viewer ---
render_text_html(text, vocab_dict, st.session_state.saved_words)

# --- Save persistent state ---
save_saved_words(st.session_state.saved_words, "default_user")
