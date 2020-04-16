def text_resume(text, maxlen, oneslice=False):
    """Resume long texts"""
    while True:
        if len(text) <= maxlen:
            return text
        text = text.split(' ')
        text = ' '.join(text[:-1]) + '...'
        if oneslice:
            return text
