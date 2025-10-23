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
        // Send the clicked word to Streamlit via postMessage
        window.parent.postMessage({{isStreamlitMessage: true, type: 'clicked_word', word: word}}, "*");
    }});
}});
</script>
"""

# --- Inject JS listener for postMessages ---
st.components.v1.html(component_code, height=400, scrolling=True)

# --- Hidden input field to receive clicked words ---
clicked = st.text_input("Last clicked word", key="clicked_word", label_visibility="collapsed")

# --- JS listener (runs outside iframe to update Streamlit input) ---
st.markdown(
    """
    <script>
    window.addEventListener("message", (event) => {
        if (event.data && event.data.type === "clicked_word") {
            const word = event.data.word;
            // set Streamlit input value
            const input = window.parent.document.querySelector('input[data-testid="stTextInput"]');
            if (input) {{
                const reactEvent = new Event("input", {{ bubbles: true }});
                input.value = word;
                input.dispatchEvent(reactEvent);
            }}
        }
    });
    </script>
    """,
    unsafe_allow_html=True,
)

# --- Process click ---
if clicked.lower() in vocab_dict:
    word = clicked.lower()
    st.session_state.saved.add(word)
    st.session_state.selected_word = word
    word_data = vocab_dict[word]

    st.markdown(f"### **{word_data['word']}**")
    st.markdown(f"**German:** {word_data['definition_german']}")
    st.markdown(f"**English:** {word_data['definition_english']}")
    if word_data.get("context_snippet"):
        st.caption(f"_{word_data['context_snippet']}_")

# --- Saved words ---
if st.session_state.saved:
    st.markdown("### 🔹 Saved Words")
    st.write(", ".join(sorted(st.session_state.saved)))
