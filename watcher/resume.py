def text_resume(text, maxlen, pattern, oneslice=False):
    """Resume long texts"""
    while True:
        if len(text) <= maxlen:
            return text
        text = text.split(pattern)
        text = pattern.join(text[:-1])
        if oneslice:
            return text
