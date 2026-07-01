class NotFoundError(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class ConflictError(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class InvalidFileTypeError(Exception):
    def __init__(self, detail: str = "Unsupported file type") -> None:
        self.detail = detail
        super().__init__(detail)


class FileTooLargeError(Exception):
    def __init__(self, detail: str = "File exceeds maximum upload size") -> None:
        self.detail = detail
        super().__init__(detail)
