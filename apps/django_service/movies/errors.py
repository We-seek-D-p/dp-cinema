class DomainError(Exception):
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(message)


class MovieNotFoundError(DomainError):
    def __init__(self, message="Movie not found"):
        super().__init__(message)


class AlreadyInWatchlistError(DomainError):
    def __init__(self, message="Movie already in list"):
        super().__init__(message)


class WatchlistItemNotFoundError(DomainError):
    def __init__(self, message="Watchlist's item not found "):
        super().__init__(message)


class PremiumContentRestrictedError(DomainError):
    def __init__(self, message="This movie requires a premium subscription"):
        super().__init__(message)
