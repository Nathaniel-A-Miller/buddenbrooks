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
if "page" not in st.session_state:  # PAGINATION
    st.session_state.page = 0

WORDS_PER_PAGE = 1000

st.title("📚 Buddenbrooks Vocabulary Reader")
st.caption("Hover over a word to see definitions. Click to save/unsave words.")

# --- Tokenize text ---
tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

# --- Pagination ---
start_idx = st.session_state.page * WORDS_PER_PAGE
end_idx = start_idx + WORDS_PER_PAGE
visible_tokens = tokens[start_idx:end_idx]

# --- Build HTML with clickable words ---
html_parts = []
for token in visible_tokens:
    key = token.strip('.,;:"!?()[]').lower()
    if key in vocab_dict:
        saved_class = "saved" if key in st.session_state.saved else ""
        html_parts.append(
            f"<span class='word {saved_class}' data-word='{key}' "
            f"data-german='{vocab_dict[key]['definition_german'].replace('\"','&quot;')}' "
            f"data-english='{vocab_dict[key]['definition_english'].replace('\"','&quot;')}'>"
            f"{token}"
            f"<span class='popover'>"
            f"<b>DE:</b> {vocab_dict[key]['definition_german']}<br>"
            f"<i>EN:</i> {vocab_dict[key]['definition_english']}"
            f"</span></span>"
        )
    else:
        html_parts.append(token)

html_content = " ".join(html_parts)

# --- CSS + JS for hover + sticky panel ---
component_code = f"""
<style>
.container {{
    display: flex;
    gap: 20px;
}}
.text-panel {{
    flex: 1;
    font-size: 18px;
    line-height: 1.6;
}}
.word {{
    position: relative;
    cursor: pointer;
    padding: 2px 3px;
    border-radius: 4px;
    transition: background-color 0.2s ease;
}}
.word:hover {{
    background-color: #fff59d;
}}
.popover {{
    display: none;
    position: absolute;
    z-index: 10;
    background: #fefefe;
    border: 1px solid #ccc;
    border-radius: 6px;
    padding: 6px 10px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.15);
    max-width: 260px;
    font-size: 14px;
    line-height: 1.4;
}}
.word:hover .popover {{
    display: block;
    top: 1.5em;
    left: 0;
}}
.saved {{
    background-color: #ffd54f !important;
}}
.sidebar {{
    width: 250px;
    position: sticky;
    top: 20px;
    height: fit-content;
    background: #f0f0f0;
    padding: 10px;
    border-radius: 8px;
}}
</style>

<div class="container">
  <div class="text-panel">
    {html_content}
  </div>
  <div class="sidebar" id="sidebar">
    <h3>🔹 Saved Words</h3>
    <ul id="saved-list"></ul>
    <button onclick="clearSaved()">Clear</button>
  </div>
</div>

<script>
let saved = new Set();

function updateSidebar() {{
    const list = document.getElementById("saved-list");
    list.innerHTML = "";
    Array.from(saved).sort().forEach(w => {{
        const li = document.createElement("li");
        li.textContent = w;
        list.appendChild(li);
    }});
}}

function clearSaved() {{
    saved.clear();
    updateSidebar();
    window.parent.postMessage({{type:'clear_all'}}, '*');
}}

document.querySelectorAll('.word').forEach(w => {{
    if (w.classList.contains('saved')) {{
        saved.add(w.dataset.word);
    }}
    w.addEventListener('click', e => {{
        const el = e.target.closest('.word');
        const word = el.dataset.word;
        const isSaved = el.classList.toggle('saved');
        if(isSaved) saved.add(word);
        else saved.delete(word);
        updateSidebar();
        window.parent.postMessage({{type:'word_click', word: word, saved: isSaved}}, '*');
    }});
}});

updateSidebar();
</script>
"""

st.components.v1.html(component_code, height=600, scrolling=True)

# --- Handle messages from JS ---
clicked_word = st.text_input("Clicked word", key="clicked", label_visibility="collapsed")

if clicked_word:
    sign = clicked_word[0]
    word = clicked_word[1:].lower() if sign in ['+', '-'] else clicked_word.lower()
    if word in vocab_dict:
        if sign == '-':
            st.session_state.saved.discard(word)
        else:
            st.session_state.saved.add(word)

# --- Pagination buttons ---
col1, col2 = st.columns(2)

with col1:
    if st.button("⬅️ Show previous 1000 words"):
        if st.session_state.page > 0:
            st.session_state.page -= 1

with col2:
    if st.button("➡️ Show next 1000 words"):
        if end_idx < len(tokens):
            st.session_state.page += 1

# col1, col2 = st.columns(2)
# with col1:
#     if st.session_state.page > 0:
#         if st.button("⬅️ Show previous 1000 words"):
#             st.session_state.page -= 1
#             st.experimental_rerun()
# with col2:
#     if end_idx < len(tokens):
#         if st.button("➡️ Show next 1000 words"):
#             st.session_state.page += 1
#             st.experimental_rerun()
