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

# --- Build HTML for visible portion ---
html_parts = []
for token in visible_tokens:
    key = token.strip('.,;:"!?()[]').lower()
    if key in vocab_dict:
        v = vocab_dict[key]
        saved_class = "saved" if key in st.session_state.saved else ""
        html_parts.append(
            f"<span class='word {saved_class}' data-word='{key}' "
            f"data-german='{v['definition_german'].replace('\"','&quot;')}' "
            f"data-english='{v['definition_english'].replace('\"','&quot;')}'>{token}</span>"
        )
    else:
        html_parts.append(token)
html = " ".join(html_parts)

# --- CSS + JS for popovers + toggle click ---
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
  {' '.join([
    f"<span class='word {'saved' if t.strip('.,;:\"!?()[]').lower() in st.session_state.saved else ''}' "
    f"data-word='{t.strip('.,;:\"!?()[]').lower()}'>"
    f"{t}"
    f"<span class='popover'>"
    f"<b>DE:</b> {vocab_dict[t.strip('.,;:\"!?()[]').lower()]['definition_german']}<br>"
    f"<i>EN:</i> {vocab_dict[t.strip('.,;:\"!?()[]').lower()]['definition_english']}"
    f"</span></span>"
    if t.strip('.,;:\"!?()[]').lower() in vocab_dict
    else t
    for t in visible_tokens
  ])}
</div>

<script>
const words = document.querySelectorAll('.word');
words.forEach(w => {{
  w.addEventListener('click', e => {{
    const el = e.target.closest('.word');
    const word = el.dataset.word;
    const isSaved = el.classList.toggle('saved'); // toggle visual state
    window.parent.postMessage({{type:'word_click', word:word, saved:isSaved}}, '*');
  }});
}});
</script>
"""

# --- Display component ---
st.components.v1.html(component_code, height=450, scrolling=True)

# --- Hidden receiver input ---
clicked_word = st.text_input("Clicked word", key="clicked", label_visibility="collapsed")

# --- JS listener to sync click events to Streamlit input ---
st.markdown("""
<script>
window.addEventListener("message", (event) => {
  if (event.data && event.data.type === "word_click") {
    const word = event.data.word;
    const isSaved = event.data.saved;
    const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
    if (input) {
      input.value = (isSaved ? "+" : "-") + word;  // prefix + or - for add/remove
      input.dispatchEvent(new Event("input", { bubbles: true }));
    }
  }
});
</script>
""", unsafe_allow_html=True)

# --- Handle click toggling in Python ---
if clicked_word:
    sign = clicked_word[0]
    word = clicked_word[1:].lower() if sign in ['+', '-'] else clicked_word.lower()
    if word in vocab_dict:
        if sign == '-':
            st.session_state.saved.discard(word)
        else:
            st.session_state.saved.add(word)
        st.session_state.selected_word = word

# --- Display selected word info ---
if st.session_state.selected_word:
    v = vocab_dict[st.session_state.selected_word]
    st.markdown(f"### **{v['word']}**")
    st.markdown(f"**German:** {v['definition_german']}")
    st.markdown(f"**English:** {v['definition_english']}")
    if v.get("context_snippet"):
        st.caption(f"_{v['context_snippet']}_")

# --- Saved list display ---
if st.session_state.saved:
    st.markdown("### 🔹 Saved Words")
    st.write(", ".join(sorted(st.session_state.saved)))

# --- PAGINATION BUTTON ---
if end_idx < len(tokens):
    if st.button("➡️ Show next 1000 words"):
        st.session_state.page += 1
        st.rerun()  # updated

if st.session_state.page > 0:
    if st.button("⬅️ Show previous 1000 words"):
        st.session_state.page -= 1
        st.rerun()  # updated
