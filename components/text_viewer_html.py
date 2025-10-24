import streamlit.components.v1 as components
import re

def render_text_html(text, vocab_dict, saved_words):
    """
    Display text with clickable words. Hover shows definitions.
    Clicking a word adds/removes it from saved_words.
    """

    tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

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

    for token in tokens:
        key = token.strip('.,;:"!?()[]').lower()
        if key in vocab_dict:
            saved_class = "saved" if key in saved_words else ""
            html += (
                f"<span class='word {saved_class}' "
                f"onclick=\"document.getElementById('clicked_word').value='{key}';"
                f"document.getElementById('clicked_word').dispatchEvent(new Event('change'))\">"
                f"{token}<span class='pop'>{vocab_dict[key]['definition_english']}</span>"
                f"</span> "
            )
        else:
            html += token + " "

    html += "</p>"

    components.html(html, height=500, scrolling=True)
