# -*- coding: utf-8 -*-
from unicodedata import normalize

def normalize_text(text, to_lower=True):
    text = normalize('NFKD', text).encode('ASCII', 'ignore')

    final_text = text

    if to_lower:
        final_text = text.lower()

    if type(final_text) == bytes:
        final_text = final_text.decode('UTF-8')

    return fix_strange_quote_chars(final_text)

def fix_strange_quote_chars(text):
        return text.replace(u'``', u'"').replace(u'\'\'', u'"')

# TODO - user original indexes
def word_tokenize(text):
    current_start_idx = 0
    current_end_idx = 0
    current_token_letters = []
    tokens = []
    spans = []
    len_text = len(text)
    for i, letter in enumerate(text):
        if letter == ' ':
            if len(current_token_letters) > 0:
                new_token = ''.join(current_token_letters)
                tokens.append(new_token)
                spans.append((current_start_idx, current_end_idx))
            current_token_letters = []
            current_start_idx = min(i + 1, len_text - 1)
            current_end_idx = min(i + 1, len_text - 1)
        else:
            if letter.isalpha():
                current_token_letters.append(letter)
            current_end_idx = i
    if len(current_token_letters) > 0:
        new_token = ''.join(current_token_letters)
        tokens.append(new_token)
        spans.append((current_start_idx, current_end_idx))

    return tokens, spans

def fix_strange_quote_chars(token):
    return token.replace(u'``', u'"').replace(u'\'\'', u'"')