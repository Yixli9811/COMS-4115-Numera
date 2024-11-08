class Token:
    def __init__(self, type, value, line_num=None):
        self.type = type
        self.value = value
        self.line_num = line_num

    def __repr__(self):
        return f"<{self.type}, {repr(self.value)}>"