import streamlit as st
import streamlit.components.v1 as components
import re

def render_text_html(text, vocab_dict, saved_words, words_per_page=1000):
    """
    Renders text with clickable words in HTML.
    saved_words: a Python set of currently saved words
    """

    # --- Session page handling ---
    if "page" not in st.session_state:
        st.session_state.page = 0
    page = st.session_state.page

    # --- Tokenize and paginate ---
    tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
    start = page * words_per_page
    end = start + words_per_page
    visible_tokens = tokens[start:end]

    st.markdown(f"### 📖 Reading: words {start+1:,}–{min(end,len(tokens)):,} of {len(tokens):,}")

    # --- Build HTML ---
    html = """
    <style>
    .word { cursor: pointer; padding:2px 3px; border-radius:3px; position: relative;}
    .word:hover { background-color: #fff59d; }
    .saved { background-color: #ffd54f !important; }
    .pop { visibility:hidden; background:#fff; border:1px solid #ccc; border-radius:4px;
           padding:4px; position:absolute; z-index:10; font-size:14px; max-width:200px; }
    .word:hover .pop { visibility: visible; top:1.2em; left:0; }
    </style>
    <p style="font-size:18px; line-height:1.6;">
    """

    for token in visible_tokens:
        key = token.strip('.,;:"!?()[]').lower()
        if key in vocab_dict:
            saved_class = "saved" if key in saved_words else ""
            html += (
                f"<span class='word {saved_class}' "
                f"onclick=\"document.getElementById('clicked_word').value='{key}'; "
                f"document.getElementById('clicked_word').dispatchEvent(new Event('change'))\">"
                f"{token}<span class='pop'>{vocab_dict[key]['definition_english']}</span>"
                f"</span> "
            )
        else:
            html += token + " "

    html += "</p>"

    # --- Render HTML in Streamlit component ---
    components.html(html, height=500, scrolling=True)
