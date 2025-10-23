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
st.caption("Hover to see German & English definitions. Click to save a word.")

# --- Tokenize text ---
tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

# --- Build HTML ---
html_parts = []
for token in tokens[:400]:
    key = token.strip('.,;:"!?()[]').lower()
    if key in vocab_dict:
        vocab = vocab_dict[key]
        tooltip = f"{vocab['definition_german']} — {vocab['definition_english']}"
        color = "#ffd54f" if key in st.session_state.saved else "transparent"
        html_parts.append(
            f"<span class='word' data-word='{key}' "
            f"title='{tooltip}' "
            f"style='background-color:{color}; padding:2px; border-radius:4px; cursor:pointer;'>"
            f"{token}</span>"
        )
    else:
        html_parts.append(token)
html = " ".join(html_parts)

# --- HTML + JS bridge ---
component_code = f"""
<div id='text' style='font-size:18px; line-height:1.6;'>{html}</div>
<script>
const words = document.querySelectorAll('.word');
words.forEach(w => {{
    w.addEventListener('click', e => {{
        const word = e.target.dataset.word;
        Streamlit.setComponentValue(word); // send to Streamlit
    }});
}});
</script>
"""

clicked_word = st.components.v1.html(
    component_code, height=400, scrolling=True, key="text_component"
)

# --- Handle click event ---
if clicked_word:
    word = clicked_word.lower()
    if word in vocab_dict:
        st.session_state.saved.add(word)
        st.session_state.selected_word = word

# --- Display selected word ---
if st.session_state.selected_word:
    data = vocab_dict[st.session_state.selected_word]
    st.markdown(f"### **{data['word']}**")
    st.markdown(f"**German:** {data['definition_german']}")
    st.markdown(f"**English:** {data['definition_english']}")
    if data.get("context_snippet"):
        st.caption(f"_{data['context_snippet']}_")

# --- Saved list ---
if st.session_state.saved:
    st.markdown("### 🔹 Saved Words")
    st.write(", ".join(sorted(st.session_state.saved)))
