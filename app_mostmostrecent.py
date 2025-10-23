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

st.title("📚 Buddenbrooks Vocabulary Reader")
st.caption("Hover to see definitions (German + English). Click to save a word.")

# --- Tokenize text ---
tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

# --- Build HTML with hover data attributes ---
html_parts = []
for token in tokens[:400]:
    key = token.strip('.,;:"!?()[]').lower()
    if key in vocab_dict:
        v = vocab_dict[key]
        html_parts.append(
            f"<span class='word' data-word='{key}' "
            f"data-german='{v['definition_german'].replace('\"','&quot;')}' "
            f"data-english='{v['definition_english'].replace('\"','&quot;')}'>{token}</span>"
        )
    else:
        html_parts.append(token)
html = " ".join(html_parts)

# --- CSS + JS for popovers + click ---
component_code = f"""
<style>
.word {{
  position: relative;
  cursor: pointer;
  padding: 2px 3px;
  border-radius: 4px;
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
    f"<span class='word' data-word='{t.strip('.,;:\"!?()[]').lower()}'>"
    f"{t}"
    f"<span class='popover'>"
    f"<b>DE:</b> {vocab_dict[t.strip('.,;:\"!?()[]').lower()]['definition_german']}<br>"
    f"<i>EN:</i> {vocab_dict[t.strip('.,;:\"!?()[]').lower()]['definition_english']}"
    f"</span></span>"
    if t.strip('.,;:\"!?()[]').lower() in vocab_dict
    else t
    for t in tokens[:400]
  ])}
</div>

<script>
const words = document.querySelectorAll('.word');
words.forEach(w => {{
  w.addEventListener('click', e => {{
    const word = e.target.closest('.word').dataset.word;
    window.parent.postMessage({{type:'word_click', word:word}}, '*');
    // visual feedback
    e.target.closest('.word').classList.add('saved');
  }});
}});
</script>
"""

# --- Inject HTML ---
st.components.v1.html(component_code, height=450, scrolling=True)

# --- Hidden receiver + handler ---
clicked_word = st.text_input("Clicked word", key="clicked", label_visibility="collapsed")

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

# --- When clicked word matches vocab, show definition ---
if clicked_word.lower() in vocab_dict:
    word = clicked_word.lower()
    st.session_state.saved.add(word)
    st.session_state.selected_word = word
    v = vocab_dict[word]
    st.markdown(f"### **{v['word']}**")
    st.markdown(f"**German:** {v['definition_german']}")
    st.markdown(f"**English:** {v['definition_english']}")
    if v.get("context_snippet"):
        st.caption(f"_{v['context_snippet']}_")

# --- Saved list ---
if st.session_state.saved:
    st.markdown("### 🔹 Saved Words")
    st.write(", ".join(sorted(st.session_state.saved)))
