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
if "page" not in st.session_state:
    st.session_state.page = 0

WORDS_PER_PAGE = 1000

st.title("📚 Buddenbrooks Vocabulary Reader")
st.caption("Hover to see definitions. Click to save/remove.")

# --- Tokenize text ---
tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
start_idx = st.session_state.page * WORDS_PER_PAGE
end_idx = start_idx + WORDS_PER_PAGE
visible_tokens = tokens[start_idx:end_idx]

# --- Build HTML with clickable spans using buttons ---
html_parts = []
for token in visible_tokens:
    key = token.strip('.,;:"!?()[]').lower()
    if key in vocab_dict:
        saved_class = "saved" if key in st.session_state.saved else ""
        # Wrap each word in a button using st.button trick
        html_parts.append(
            f"<button class='word {saved_class}' data-word='{key}' "
            f"title='DE: {vocab_dict[key]['definition_german']} | EN: {vocab_dict[key]['definition_english']}'>"
            f"{token}</button>"
        )
    else:
        html_parts.append(token)
html_content = " ".join(html_parts)

# --- CSS for hover/tooltips ---
css = """
<style>
.word {
  background:none;
  border:none;
  cursor:pointer;
  padding:2px 3px;
  border-radius:4px;
  font-size:18px;
}
.word.saved {
  background-color:#ffd54f;
}
.word:hover {
  background-color:#fff59d;
}
</style>
"""

st.components.v1.html(css + f"<div>{html_content}</div>", height=450, scrolling=True)

# --- Sidebar: saved words ---
st.sidebar.header("🔹 Saved Vocabulary")
if st.session_state.saved:
    for w in sorted(st.session_state.saved):
        v = vocab_dict[w]
        st.sidebar.markdown(f"**{v['word']}**  \n_DE:_ {v['definition_german']}  \n_EN:_ {v['definition_english']}")
else:
    st.sidebar.caption("No words saved yet.")

# --- Pagination buttons ---
col1, col2 = st.columns(2)
with col1:
    if st.session_state.page > 0:
        if st.button("⬅️ Show previous 1000 words"):
            st.session_state.page -= 1
            st.rerun()
with col2:
    if end_idx < len(tokens):
        if st.button("➡️ Show next 1000 words"):
            st.session_state.page += 1
            st.rerun()
