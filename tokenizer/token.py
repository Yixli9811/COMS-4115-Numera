class Token:
    def __init__(self, type, value, start_pos=None):
        self.type = type
        self.value = value
        self.start_pos = start_pos

    def __repr__(self):
        return f"<{self.type}, {repr(self.value)}>"