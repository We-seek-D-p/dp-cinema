from apps.django_service.common.errors import DomainError


class MovieNotFoundError(DomainError):
    default_code = 'movie_not_found'
    default_message = 'Movie not found'
    http_status_code = 404


class AlreadyInWatchlistError(DomainError):
    default_code = 'already_in_watchlist'
    default_message = 'Movie already in watchlist'
    http_status_code = 400


class WatchlistItemNotFoundError(DomainError):
    default_code = 'watchlist_item_not_found'
    default_message = 'Watchlist item not found'
    http_status_code = 404


class PremiumContentRestrictedError(DomainError):
    default_code = 'premium_content_restricted'
    default_message = 'Premium content restricted'
    http_status_code = 403