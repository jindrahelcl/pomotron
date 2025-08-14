from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from sounds import sounds

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
    def __init__(self):
        kb = KeyBindings()

        # Override default key bindings to add sound
        @kb.add('<any>')
        @erring_handler
        def handle_any(event):
            sounds.play_keypress()
            # Insert the character manually
            event.app.current_buffer.insert_text(event.data)

        @kb.add('left')
        @erring_handler
        def handle_left(event):
            sounds.play_keypress()
            event.app.current_buffer.cursor_left()

        @kb.add('right')
        @erring_handler
        def handle_right(event):
            sounds.play_keypress()
            event.app.current_buffer.cursor_right()

        @kb.add('up')
        @erring_handler
        def handle_up(event):
            sounds.play_keypress()
            event.app.current_buffer.history_backward()

        @kb.add('down')
        @erring_handler
        def handle_down(event):
            sounds.play_keypress()
            event.app.current_buffer.history_forward()

        @kb.add('backspace')
        @erring_handler
        def handle_backspace(event):
            sounds.play_keypress()
            event.app.current_buffer.delete_before_cursor()

        @kb.add('delete')
        @erring_handler
        def handle_delete(event):
            sounds.play_keypress()
            event.app.current_buffer.delete()

        @kb.add('home')
        @erring_handler
        def handle_home(event):
            sounds.play_keypress()
            event.app.current_buffer.cursor_position = 0

        @kb.add('end')
        @erring_handler
        def handle_end(event):
            sounds.play_keypress()
            event.app.current_buffer.cursor_position = len(event.app.current_buffer.text)

        @kb.add('c-left')
        @erring_handler
        def handle_ctrl_left(event):
            sounds.play_keypress()
            event.app.current_buffer.cursor_left(count=event.app.current_buffer.document.find_previous_word_beginning())

        @kb.add('c-right')
        @erring_handler
        def handle_ctrl_right(event):
            sounds.play_keypress()
            event.app.current_buffer.cursor_right(count=event.app.current_buffer.document.find_next_word_ending())

        @kb.add('m-backspace')
        @erring_handler
        def handle_alt_backspace(event):
            sounds.play_keypress()
            event.app.current_buffer.delete_before_cursor(count=event.app.current_buffer.document.find_previous_word_beginning())

        @kb.add('c-delete')
        @erring_handler
        def handle_ctrl_delete(event):
            sounds.play_keypress()
            event.app.current_buffer.delete(count=event.app.current_buffer.document.find_next_word_ending())

        self.prompt_session = PromptSession(key_bindings=kb)

    def play_keypress(self):
        sounds.play_keypress()

    def prompt(self):
        try:
            return self.prompt_session.prompt("pomo> ")
        except HandlerError as e:
            raise e.error
        except KeyboardInterrupt:
            return ""
