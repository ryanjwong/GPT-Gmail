class Email:
    def __init__(self, id, subject, body, labels) -> None:
        self.id = id
        self.subject = subject
        self.body = body
        self.labels = labels