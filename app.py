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
if "selected_word" not in st.session_state:
    st.session_state.selected_word = None
if "saved" not in st.session_state:
    st.session_state.saved = set()

st.title("📚 Buddenbrooks Vocabulary Reader")
st.caption("Hover to see definition. Click a word to save it and see full info below.")

# --- Tokenize text ---
tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

# --- Build HTML with hover and click ---
html_parts = []
for i, token in enumerate(tokens[:400]):  # first 400 tokens for speed
    key = token.strip('.,;:"!?()[]').lower()
    if key in vocab_dict:
        # check if saved
        color = "#ffd54f" if key in st.session_state.saved else "transparent"
        html_parts.append(
            f"<span class='word' data-word='{key}' title='{vocab_dict[key]['definition_german']}' "
            f"style='background-color:{color}; cursor:pointer;'>{token}</span>"
        )
    else:
        html_parts.append(token)
html = " ".join(html_parts)

# --- CSS & JS for interactivity ---
component_code = f"""
<div id='text' style='font-size:18px; line-height:1.6;'>{html}</div>
<script>
const words = document.querySelectorAll('.word');
words.forEach(w => {{
    w.addEventListener('click', e => {{
        const word = e.target.dataset.word;
        // send to Streamlit via window.postMessage
        window.parent.postMessage({{type:'word_click', word: word}}, '*');
    }});
}});
</script>
"""

# --- Display text ---
st.components.v1.html(component_code, height=400, scrolling=True)

# --- Show saved word definition below ---
st.subheader("📝 Saved Words / Clicked Word")

# Instructions for manual input (simple Streamlit bridge)
clicked_word = st.text_input(
    "Type or click a word:", st.session_state.selected_word or ""
)

if clicked_word.lower() in vocab_dict:
    word_data = vocab_dict[clicked_word.lower()]
    st.session_state.selected_word = clicked_word.lower()
    st.session_state.saved.add(clicked_word.lower())

    st.markdown(f"**Word:** {word_data['word']}")
    st.markdown(f"**German:** {word_data['definition_german']}")
    st.markdown(f"**English:** {word_data['definition_english']}")
    st.caption(word_data.get("context_snippet", ""))

# Optional: show all saved words
if st.session_state.saved:
    st.markdown("### 🔹 Saved Words")
    st.write(", ".join(sorted(st.session_state.saved)))
