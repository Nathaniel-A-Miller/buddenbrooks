import streamlit as st

def render_pagination(tokens, words_per_page=1000):
    if "page" not in st.session_state:
        st.session_state.page = 0

    page = st.session_state.page
    total_pages = (len(tokens) - 1) // words_per_page + 1

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous") and page > 0:
            st.session_state.page -= 1
            st.rerun()
    with col2:
        st.write(f"Page {page + 1} / {total_pages}")
    with col3:
        if st.button("Next ➡️") and (page + 1) * words_per_page < len(tokens):
            st.session_state.page += 1
            st.rerun()
