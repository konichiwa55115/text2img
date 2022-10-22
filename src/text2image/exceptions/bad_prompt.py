from email import message


class BadPrompt(Exception):
    message = None

    def __init__(self, message):
        super().__init__(message)

        self.message = message
