class ParserError(Exception):
    def __init__(self, message):
        super().__init__(f"ParserError: {message}")
        