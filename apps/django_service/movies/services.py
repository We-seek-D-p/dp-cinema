from django.db.models import QuerySet
from .errors import (
    MovieNotFoundError,
    AlreadyInWatchlistError,
    PremiumContentRestrictedError,
    WatchlistItemNotFoundError,
)
from .models import Watchlist
from .repositories import WatchListRepository, MovieRepository
from users.models import User


class WatchListService:
    def __init__(self):
        self.watchlist_repo = WatchListRepository()
        self.movie_repo = MovieRepository()

    def add_to_watchlist(self, user: User, movie_id: int) -> Watchlist:
        movie = self.movie_repo.get_by_id(movie_id)
        if not movie:
            raise MovieNotFoundError()

        if self.watchlist_repo.exists(user, movie_id):
            raise AlreadyInWatchlistError()

        if not user.is_premium and movie.is_premium:
            raise PremiumContentRestrictedError()

        return self.watchlist_repo.create_or_restore(user, movie_id)

    def get_user_watchlist(self, user: User) -> QuerySet[Watchlist, Watchlist]:
        return self.watchlist_repo.get_user_watchlist(user)

    def remove_from_watchlist(self, user: User, movie_id: int):
        watchlist = self.watchlist_repo.get_item(user, movie_id)
        if not watchlist:
            raise WatchlistItemNotFoundError()

        self.watchlist_repo.delete(watchlist)
