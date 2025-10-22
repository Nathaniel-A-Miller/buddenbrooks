import streamlit as st
import json, re, pandas as pd
from pathlib import Path

TEXT_PATH = Path("text/buddenbrooks_ch1.txt")
VOCAB_PATH = Path("vocab/vocab_ch1.json")

# --- Load data ---
with open(TEXT_PATH, encoding="utf-8") as f:
    text = f.read()
with open(VOCAB_PATH, encoding="utf-8") as f:
    vocab_list = json.load(f)
vocab_dict = {v["word"].lower(): v for v in vocab_list}

# --- Session state ---
saved = st.session_state.setdefault("saved", set())

st.title("📚 Buddenbrooks Vocabulary Reader")
st.caption("Click words to highlight and add them to your list.")

# --- Tokenize ---
tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

# --- Inline clickable words ---
def render_word(token, idx):
    word = token.strip('.,;:"!?()[]').lower()
    is_saved = word in saved
    style = (
        "background-color:#fff3b0; color:black; border:none; padding:0 3px; "
        "border-radius:3px;"
        if is_saved
        else "background:none; color:black; border:none; padding:0 3px;"
    )
    clicked = st.button(
        token,
        key=f"{word}_{idx}",
        help=vocab_dict.get(word, {}).get("definition_german", ""),
    )
    if clicked:
        if word not in saved:
            saved.add(word)
        else:
            saved.remove(word)  # toggle off
    st.markdown(
        f"<style>div[data-testid='stButton'] button#{word}_{idx} {{{style}}}</style>",
        unsafe_allow_html=True,
    )

cols = st.columns(10)
for i, token in enumerate(tokens[:400]):
    with cols[i % 10]:
        render_word(token, i)

st.divider()

# --- Saved list ---
st.subheader("📝 Saved Words")
if saved:
    rows = []
    for w in sorted(saved):
        e = vocab_dict.get(w, {})
        rows.append(
            [w, e.get("definition_german", ""), e.get("definition_english", ""), e.get("context_snippet", "")]
        )
    st.dataframe(pd.DataFrame(rows, columns=["Word", "German", "English", "Context"]), use_container_width=True)
    if st.button("Clear Saved Words"):
        saved.clear()
else:
    st.info("No words selected yet.")
