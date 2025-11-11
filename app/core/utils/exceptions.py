from fastapi import status

class AppBaseException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "An unexpected error occurred"

    def __init__(self, detail: str|None = None):
        if detail:
            self.detail


class ValidationError(AppBaseException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid input"

class DatabaseError(AppBaseException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail ="A database error has occurred"

class NotFoundError(AppBaseException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"