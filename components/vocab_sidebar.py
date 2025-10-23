import streamlit as st

def render_vocab_sidebar(saved_words, vocab_dict):
    st.sidebar.header("📘 Saved Vocabulary")
    if saved_words:
        for word in sorted(saved_words):
            v = vocab_dict[word]
            st.sidebar.markdown(f"**{word}** — {v['definition_english']}")
        if st.sidebar.button("Clear Saved Words"):
            saved_words.clear()
    else:
        st.sidebar.info("No words saved yet.")
