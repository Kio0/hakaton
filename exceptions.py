class UserExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class WrongPasswordError(Exception):
    pass


class ServiceNotFoundError(Exception):
    pass
