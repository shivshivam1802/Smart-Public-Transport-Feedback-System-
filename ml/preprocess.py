import re
def clean_text(text):
    return re.sub(r"[^a-zA-Z\s]", "", text.lower())
