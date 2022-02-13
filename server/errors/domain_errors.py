from typing import Protocol


class IBusinessError(Protocol):
    message: str
    internal_code: int


class Error(Exception):
    def __init__(self, value=""):
        if not hasattr(self, "value"):
            self.value = value

    def __str__(self):
        return repr(self.value)


class UsernameAlreadyExistsError(Error):
    message = "An account with this username already exists."
    internal_code = 40901


class EmailAddressAlreadyExistsError(Error):
    message = "An account with this email address already exists."
    internal_code = 40902


class TermsNotAcceptedError(Error):
    message = "You must accept the terms of service."
    internal_code = 42901


class UserDoesNotExistsError(Error):
    message = "User does not exists."
    internal_code = 40401


class CannotEditUserError(Error):
    message = "You can not edit the user due to insufficient privileges"
    internal_code = 40301


class YouCannotDeleteYourselfError(Error):
    message = "You can not delete yourself."
    internal_code = 40001
