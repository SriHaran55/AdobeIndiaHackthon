def classify_headings(text):
    text_len = len(text.strip())
    if text_len < 20 and text.isupper():
        return "H1"
    elif text_len < 40:
        return "H2"
    elif text_len < 60:
        return "H3"
    return None
