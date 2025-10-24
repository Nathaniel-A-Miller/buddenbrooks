import streamlit as st
from utils.loader import load_text, load_vocab
from components.text_viewer_html import render_text_html
from components.vocab_sidebar import render_vocab_sidebar
from components.pagination import render_pagination
from utils.storage import load_saved_words, save_saved_words

st.set_page_config(page_title="Buddenbrooks Reader", layout="wide")

# --- Load data ---
TEXT_PATH = "data/text/buddenbrooks_ch1.txt"
VOCAB_PATH = "data/vocab/vocab_ch1.json"

text = load_text(TEXT_PATH)
vocab_dict = load_vocab(VOCAB_PATH)
tokens = text.split()  # for pagination only

# --- Load saved words ---
if "saved_words" not in st.session_state:
    st.session_state.saved_words = load_saved_words("default_user")

# --- Hidden input to capture clicked words ---
clicked_word = st.text_input("", key="clicked_word", value="", label_visibility="collapsed")
if clicked_word:
    word = clicked_word.lower()
    if word in st.session_state.saved_words:
        st.session_state.saved_words.remove(word)
    else:
        st.session_state.saved_words.add(word)
    st.session_state.clicked_word = ""  # reset input

# --- Sidebar ---
render_vocab_sidebar(st.session_state.saved_words, vocab_dict)

# --- Render HTML text viewer ---
render_text_html(text, vocab_dict, st.session_state.saved_words)

# --- Pagination ---
render_pagination(tokens)

# --- Save session to disk ---
save_saved_words(st.session_state.saved_words, "default_user")
