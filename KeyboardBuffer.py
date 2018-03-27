import Tkinter as tk
from collections import deque
"""
	Buffer using a queqe to proplerly process keyboard in
"""


class KeyboardBuffer(tk.Tk):

	def __init__(self):
        self.buffer = deque()

    def emptyBuffer(self):
        while len(self.buffer) != 0:
            return buffer.popleft()
    """
		Strip character and append it to the buffer
	Args:
		event: Tk keyboard event. Passed when bound to a key
	"""
    def buffer_keys(event):
        buffer.append(str.replace(repr(event.char), '\'', ''))
