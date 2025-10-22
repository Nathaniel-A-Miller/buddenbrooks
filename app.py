import streamlit as st
import json
import re

# --- Load data ---
text = open("buddenbrooks_excerpt.txt", encoding="utf-8").read()
with open("vocab.json", encoding="utf-8") as f:
    vocab = json.load(f)
vocab_dict = {v["word"].lower(): v for v in vocab}

# --- Session state ---
if "selected_word" not in st.session_state:
    st.session_state.selected_word = None

# --- Build HTML with clickable spans ---
def make_html(text, vocab):
    words = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
    html = ""
    for i, w in enumerate(words):
        clean = w.strip(".,;:!?\"()[]").lower()
        if clean in vocab:
            html += f"<span class='word' id='{clean}'>{w}</span> "
        else:
            html += w + " "
    return html

# --- Custom CSS & JS ---
st.markdown("""
<style>
.word {
  cursor: pointer;
  color: #0044cc;
}
.word:hover {
  background-color: #e6f2ff;
}
.selected {
  background-color: #ffd54f;
}
</style>
""", unsafe_allow_html=True)

html = make_html(text, vocab_dict)

# --- HTML block with click handler ---
component_code = f"""
<div id='text'>{html}</div>
<script>
const words = document.querySelectorAll('.word');
words.forEach(w => {{
  w.addEventListener('click', e => {{
    const word = e.target.id;
    window.parent.postMessage({{word: word}}, '*');
  }});
}});
</script>
"""

clicked = st.components.v1.html(component_code, height=400, scrolling=True)

# --- Listen for click event ---
st.markdown("### Definition")

# The following uses Streamlit’s message listener (requires a Streamlit reload hook)
# For simplicity, we’ll simulate manual word lookup for now
selected_word = st.text_input("Type or click a word:", st.session_state.selected_word or "")
if selected_word.lower() in vocab_dict:
    v = vocab_dict[selected_word.lower()]
    st.write(f"**{v['word']}**")
    st.write(f"**German:** {v['definition_german']}")
    st.write(f"**English:** {v['definition_english']}")
    st.caption(v['context_snippet'])
