import streamlit as st
from utils.loader import load_text, load_vocab
from utils.tokenizer import tokenize
from components.text_viewer import render_text
from components.vocab_sidebar import render_vocab_sidebar
from components.pagination import render_pagination

st.set_page_config(page_title="Buddenbrooks Reader", layout="wide")

# --- Load Data ---
TEXT_PATH = "data/text/buddenbrooks_ch1.txt"
VOCAB_PATH = "data/vocab/vocab_ch1.json"

text = load_text(TEXT_PATH)
vocab_dict = load_vocab(VOCAB_PATH)
tokens = tokenize(text)

# --- Session State ---
if "saved_words" not in st.session_state:
    st.session_state.saved_words = set()

# --- Sidebar ---
render_vocab_sidebar(st.session_state.saved_words, vocab_dict)

# --- Text and Pagination ---
render_text(text, vocab_dict, st.session_state.saved_words)
render_pagination(tokens)
