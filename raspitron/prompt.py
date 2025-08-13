from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings

# Helper class to make exceptions from keypress handlers propagate
class HandlerError(KeyboardInterrupt):
    def __init__(self, error):
        self.error = error

# Decorator to make exceptions from keypress handlers propagate
def erring_handler(fn):
    def wrapped(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except BaseException as e:
            raise HandlerError(e)
    return wrapped

class Session:
    def __init__(self, sentence_cb):
        self.sentence_cb = sentence_cb
        kb = KeyBindings()
        for char in ".!?":
            kb.add(char)(self.onpunctuation)
        self.prompt_session = PromptSession(key_bindings=kb)

    @erring_handler
    def onpunctuation(self, event):
        buf = event.app.current_buffer
        key = event.key_sequence[0].key
        buf.insert_text(key)
        text = buf.text
        pos = buf.cursor_position
        sentence = self.extract_sentence(text, pos)
        self.sentence_cb(sentence)

    def extract_sentence(self, buffer_text, cursor_pos):
        text = buffer_text[:cursor_pos - 1]
        rev_iter = zip(reversed(text), reversed(range(len(text))))
        start = 1 + next((pos for ch, pos in rev_iter if ch in '.!?'), -1)
        return buffer_text[start:cursor_pos]

    def prompt(self):
        try:
            return self.prompt_session.prompt("pomo> ")
        except HandlerError as e:
            raise e.error
        except KeyboardInterrupt:
            pass
