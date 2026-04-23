from apps.django_service.common.errors import DomainError
from rest_framework import status


class MovieNotFoundError(DomainError):
    default_code = "movie_not_found"
    default_message = "Movie not found"
    http_status_code = status.HTTP_404_NOT_FOUND


class AlreadyInWatchlistError(DomainError):
    default_code = "already_in_watchlist"
    default_message = "Movie already in watchlist"
    http_status_code = status.HTTP_400_BAD_REQUEST


class WatchlistItemNotFoundError(DomainError):
    default_code = "watchlist_item_not_found"
    default_message = "Watchlist item not found"
    http_status_code = status.HTTP_404_NOT_FOUND


class PremiumContentRestrictedError(DomainError):
    default_code = "premium_content_restricted"
    default_message = "Premium content restricted"
    http_status_code = status.HTTP_403_FORBIDDEN
