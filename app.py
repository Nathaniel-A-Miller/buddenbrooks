import streamlit as st
import json
import re
from pathlib import Path

# --- Load text and vocab ---
TEXT_PATH = Path("text/buddenbrooks_ch1.txt")
VOCAB_PATH = Path("vocab/vocab_ch1.json")

text = TEXT_PATH.read_text(encoding="utf-8")
vocab_list = json.loads(VOCAB_PATH.read_text(encoding="utf-8"))
vocab_dict = {v["word"].lower(): v for v in vocab_list}

# --- Session state ---
if "saved" not in st.session_state:
    st.session_state.saved = set()
if "page" not in st.session_state:  # PAGINATION
    st.session_state.page = 0

WORDS_PER_PAGE = 1000  # PAGINATION

st.title("📚 Buddenbrooks Vocabulary Reader")
st.caption("Hover to see definitions (German + English). Click to save or unclick to remove.")

# --- Tokenize text ---
tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

# --- PAGINATION LOGIC ---
start_idx = st.session_state.page * WORDS_PER_PAGE
end_idx = start_idx + WORDS_PER_PAGE
visible_tokens = tokens[start_idx:end_idx]

# --- Render tokens as Streamlit buttons with hover tooltip ---
cols_per_row = 8  # adjust for wrapping
cols = st.columns(cols_per_row)

for i, token in enumerate(visible_tokens):
    key = token.strip('.,;:"!?()[]').lower()
    if key in vocab_dict:
        v = vocab_dict[key]
        label = token
        is_saved = key in st.session_state.saved

        # Use tooltip for hover definition
        if cols[i % cols_per_row].button(
            label, 
            key=f"btn_{start_idx+i}", 
            help=f"DE: {v['definition_german']}\nEN: {v['definition_english']}"
        ):
            if is_saved:
                st.session_state.saved.discard(key)
            else:
                st.session_state.saved.add(key)

# --- Display selected word info if clicked in main area (optional) ---
if st.session_state.saved:
    last_word = list(st.session_state.saved)[-1]
    v = vocab_dict[last_word]
    st.markdown(f"### **{v['word']}**")
    st.markdown(f"**German:** {v['definition_german']}")
    st.markdown(f"**English:** {v['definition_english']}")
    if v.get("context_snippet"):
        st.caption(f"_{v['context_snippet']}_")

# --- SIDEBAR: Saved words ---
st.sidebar.header("🔹 Saved Vocabulary")
if st.session_state.saved:
    for w in sorted(st.session_state.saved):
        v = vocab_dict[w]
        st.sidebar.markdown(
            f"**{v['word']}**  \n_DE:_ {v['definition_german']}  \n_EN:_ {v['definition_english']}"
        )
else:
    st.sidebar.caption("No words saved yet. Click words in the text to save them.")

# --- PAGINATION BUTTONS ---
col1, col2 = st.columns(2)
with col1:
    if st.session_state.page > 0:
        if st.button("⬅️ Show previous 1000 words"):
            st.session_state.page -= 1
            st.experimental_rerun()
with col2:
    if end_idx < len(tokens):
        if st.button("➡️ Show next 1000 words"):
            st.session_state.page += 1
            st.experimental_rerun()
