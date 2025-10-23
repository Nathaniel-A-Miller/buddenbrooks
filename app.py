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
if "selected_word" not in st.session_state:
    st.session_state.selected_word = None
if "page" not in st.session_state:  # Pagination
    st.session_state.page = 0

WORDS_PER_PAGE = 1000

st.title("📚 Buddenbrooks Vocabulary Reader")
st.caption("Hover to see definitions (German + English). Click a word to select it, then use the button to save/remove it.")

# --- Tokenize text ---
tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

# --- Pagination logic ---
start_idx = st.session_state.page * WORDS_PER_PAGE
end_idx = start_idx + WORDS_PER_PAGE
visible_tokens = tokens[start_idx:end_idx]

# --- Build HTML for visible portion ---
html_parts = []
for token in visible_tokens:
    key = token.strip('.,;:"!?()[]').lower()
    if key in vocab_dict:
        saved_class = "saved" if key in st.session_state.saved else ""
        html_parts.append(
            f"<span class='word {saved_class}' data-word='{key}'>"
            f"{token}"
            f"<span class='popover'>"
            f"<b>DE:</b> {vocab_dict[key]['definition_german']}<br>"
            f"<b>EN:</b> {vocab_dict[key]['definition_english']}"
            f"</span></span>"
        )
    else:
        html_parts.append(token)
html = " ".join(html_parts)

# --- CSS + JS ---
component_code = f"""
<style>
.word {{
  position: relative;
  cursor: pointer;
  padding: 2px 3px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}}
.word:hover {{
  background-color: #fff59d;
}}
.popover {{
  display: none;
  position: absolute;
  z-index: 10;
  background: #fefefe;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 6px 10px;
  box-shadow: 2px 2px 6px rgba(0,0,0,0.15);
  max-width: 260px;
  font-size: 14px;
  line-height: 1.4;
}}
.word:hover .popover {{
  display: block;
  top: 1.5em;
  left: 0;
}}
.saved {{
  background-color: #ffd54f !important;
}}
</style>

<div id="text" style="font-size:18px; line-height:1.6;">
  {html}
</div>

<script>
const words = document.querySelectorAll('.word');
words.forEach(w => {{
  w.addEventListener('click', e => {{
    const el = e.target.closest('.word');
    const word = el.dataset.word;
    window.parent.postMessage({{type:'word_click', word:word}}, '*');
  }});
}});
</script>
"""

st.components.v1.html(component_code, height=450, scrolling=True)

# --- Hidden input for syncing clicks ---
clicked_word = st.text_input("", key="clicked_word_hidden", label_visibility="collapsed")

# --- JS listener to update hidden input ---
st.markdown("""
<script>
window.addEventListener("message", (event) => {
  if (event.data && event.data.type === "word_click") {
    const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
    if (input) {
      input.value = event.data.word;
      input.dispatchEvent(new Event("input", { bubbles: true }));
    }
  }
});
</script>
""", unsafe_allow_html=True)

# --- Handle word selection ---
if clicked_word:
    word = clicked_word.lower()
    if word in vocab_dict:
        st.session_state.selected_word = word

# --- Selected word info + Add/Remove button ---
if st.session_state.selected_word:
    word = st.session_state.selected_word
    v = vocab_dict[word]
    
    st.markdown(f"### **{v['word']}**")
    st.markdown(f"**German:** {v['definition_german']}") 
    st.markdown(f"**English:** {v['definition_english']}")
    if v.get("context_snippet"):
        st.caption(f"_{v['context_snippet']}_")
    
    # Add/Remove button
    if word in st.session_state.saved:
        if st.button(f"❌ Remove '{v['word']}' from saved"):
            st.session_state.saved.discard(word)
    else:
        if st.button(f"➕ Add '{v['word']}' to saved"):
            st.session_state.saved.add(word)

# --- Sidebar: Saved words ---
st.sidebar.header("🔹 Saved Vocabulary")
if st.session_state.saved:
    for w in sorted(st.session_state.saved):
        v = vocab_dict[w]
        st.sidebar.markdown(f"**{v['word']}**  \n_DE:_ {v['definition_german']}  \n_EN:_ {v['definition_english']}")
else:
    st.sidebar.caption("No words saved yet. Click words in the text to select them and use the button to save.")

# --- Pagination buttons ---
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
