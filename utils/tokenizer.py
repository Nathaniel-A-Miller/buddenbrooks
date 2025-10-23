import re

def tokenize(text: str):
    return re.findall(r"\w+|[^\w\s]", text, re.UNICODE)

def get_visible_tokens(tokens, page, words_per_page=1000):
    start = page * words_per_page
    end = start + words_per_page
    return tokens[start:end], start, end
