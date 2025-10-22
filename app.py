import streamlit as st
import json
import re
import pandas as pd
from pathlib import Path
import streamlit.components.v1 as components

# ====== PATHS ======
TEXT_PATH = Path("text/buddenbrooks_ch1.txt")
VOCAB_PATH = Path("vocab/vocab_ch1.json")

# ====== LOAD DATA ======
with open(TEXT_PATH, "r", encoding="utf-8") as f:
    text = f.read()

with open(VOCAB_PATH, "r", encoding="utf-8") as f:
    vocab_list = json.load(f)

vocab_dict = {v["word"].lower(): v for v in vocab_list}

# ====== SESSION STATE ======
if "saved" not in st.session_state:
    st.session_state.saved = set()
if "clicked_word" not in st.session_state:
    st.session_state.clicked_word = None

st.title("📚 Buddenbrooks Vocabulary Reader")

st.caption(
    "Click any word in the text to highlight it and add it to your memorization list below."
)

# ====== TOKENIZE ======
tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

# ====== BUILD HTML TEXT WITH CLICKABLE WORDS ======
html_parts = []
for i, token in enumerate(tokens[:400]):  # show first 400 tokens for performance
    key = token.strip('.,;:"!?()[]').lower()
    is_saved = key in st.session_state.saved
    color = "#fff3b0" if is_saved else "transparent"
    html_parts.append(
        f"<span class='word' data-word='{key}' "
        f"style='background-color:{color}; cursor:pointer;'>{token}</span>"
    )

html = " ".join(html_parts)

# ====== HTML & JAVASCRIPT FOR CLICK DETECTION ======
js_code = """
<script>
const words = Array.from(window.parent.document.querySelectorAll('.word'));
words.forEach(el => {
  el.addEventListener('click', event => {
    const w = event.target.dataset.word;
    window.parent.postMessage({ type: 'word_click', word: w }, '*');
  });
});
</script>
"""

# Display text block
components.html(
    f"""
    <div style='font-size:18px; line-height:1.7; text-align:justify;'>
        {html}
    </div>
    {js_code}
    """,
    height=400,
)

# ====== HANDLE MESSAGE FROM JS ======
# This trick works by having the user click “Rerun” when Streamlit detects state change
clicked = st.query_params.get("word", None)
if clicked and clicked not in st.session_state.saved:
    st.session_state.saved.add(clicked.lower())

# ====== DISPLAY SAVED WORDS ======
st.divider()
st.subheader("📝 Saved Words")

if st.session_state.saved:
    rows = []
    for word in sorted(st.session_state.saved):
        entry = vocab_dict.get(word)
        if entry:
            rows.append(
                [
                    entry["word"],
                    entry.get("definition_german", ""),
                    entry.get("definition_english", ""),
                    entry.get("context_snippet", ""),
                ]
            )
        else:
            rows.append([word, "", "", ""])
    df = pd.DataFrame(rows, columns=["Word", "German", "English", "Context"])
    st.dataframe(df, use_container_width=True)

    if st.button("Clear Saved Words"):
        st.session_state.saved = set()
else:
    st.info("No words selected yet. Click on a word in the text above to save it.")
