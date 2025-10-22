import streamlit as st
import json
import re
import pandas as pd
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

st.title("📚 Buddenbrooks Vocabulary Reader")
st.caption("Hover to see definition. Click a word to highlight and save it.")

# --- Tokenize ---
tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

# --- Render inline clickable words ---
inline_html = ""
for i, token in enumerate(tokens[:400]):  # first 400 tokens
    key = token.strip('.,;:"!?()[]').lower()
    if key in vocab_dict:
        color = "#ffd54f" if key in st.session_state.saved else "transparent"
        # Wrap each word in a form with a submit button for Streamlit
        inline_html += f"""
        <form method="post">
            <button name="word" value="{key}" style="
                background-color:{color};
                border:none;
                cursor:pointer;
                padding:0 2px;
                font-size:18px;
            " title="{vocab_dict[key]['definition_german']}">
                {token}
            </button>
        </form>
        """
    else:
        inline_html += token + " "

st.markdown(inline_html, unsafe_allow_html=True)

# --- Detect clicks via st.experimental_get_query_params ---
clicked_word = st.experimental_get_query_params().get("word")
if clicked_word:
    clicked_word = clicked_word[0]
    st.session_state.saved.add(clicked_word)

# --- Show saved words with definitions ---
if st.session_state.saved:
    rows = []
    for w in sorted(st.session_state.saved):
        v = vocab_dict.get(w, {})
        rows.append([w, v.get("definition_german", ""), v.get("definition_english", ""), v.get("context_snippet", "")])
    df = pd.DataFrame(rows, columns=["Word", "German", "English", "Context"])
    st.subheader("📝 Saved Words")
    st.dataframe(df, use_container_width=True)
    if st.button("Clear Saved Words"):
        st.session_state.saved.clear()
else:
    st.info("No words selected yet. Click a word to save it.")
