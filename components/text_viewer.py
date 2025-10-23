import streamlit as st
from utils.tokenizer import tokenize, get_visible_tokens

def render_text(text, vocab_dict, saved_words, words_per_page=1000):
    tokens = tokenize(text)
    page = st.session_state.get("page", 0)
    visible, start, end = get_visible_tokens(tokens, page, words_per_page)

    st.markdown("### 📖 Reading")
    st.caption(f"Words {start+1:,}–{min(end, len(tokens)):,} of {len(tokens):,}")

    clicked_word = st.radio(
        "Click a word to save or unsave it:",
        ["(none)"] + [t for t in visible if t.strip(".,!?").lower() in vocab_dict],
        label_visibility="collapsed",
        horizontal=True,
        index=0
    )

    if clicked_word and clicked_word != "(none)":
        key = clicked_word.strip(".,!?").lower()
        if key in saved_words:
            saved_words.remove(key)
        else:
            saved_words.add(key)

    html = ""
    for token in visible:
        key = token.strip(".,!?").lower()
        if key in vocab_dict:
            if key in saved_words:
                html += f"<span style='background-color:#ffe082;padding:1px 3px;border-radius:3px;'>{token}</span> "
            else:
                html += f"<span style='color:#1565c0;cursor:pointer;'>{token}</span> "
        else:
            html += token + " "

    st.markdown(html, unsafe_allow_html=True)
