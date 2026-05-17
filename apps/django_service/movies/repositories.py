from django.db.models import QuerySet
from django.utils import timezone
from users.models import User

from .models import Movie, Watchlist


class MovieRepository:
    def get_published(self) -> QuerySet[Movie, Movie]:
        return Movie.objects.filter(is_published=True, deleted_at__isnull=True)

    def get_active(self) -> QuerySet[Movie, Movie]:
        return Movie.objects.filter(deleted_at__isnull=True)

    def get_by_id(self, movie_id: int) -> Movie | None:
        return self.get_published().filter(id=movie_id).first()

    def get_by_id_internal(self, movie_id: int) -> Movie | None:
        return self.get_active().filter(id=movie_id).first()

    def update_source_url(self, movie: Movie, source_url: str) -> Movie:
        movie.source_url = source_url
        movie.save()
        return movie

    def finalize_movie(self, movie: Movie, hls_url: str):
        movie.hls_url = hls_url
        movie.is_published = True
        movie.save()
        return movie


class WatchListRepository:
    def get_user_watchlist(self, user: User) -> QuerySet[Watchlist, Watchlist]:
        return Watchlist.objects.filter(
            user=user, deleted_at__isnull=True
        ).select_related("movie")

    def get_item(self, user: User, movie_id: int) -> Watchlist | None:
        return self.get_user_watchlist(user).filter(movie_id=movie_id).first()

    def exists(self, user: User, movie_id: int) -> bool:
        return self.get_user_watchlist(user).filter(movie_id=movie_id).exists()

    def create_or_restore(self, user: User, movie_id: int) -> Watchlist:
        item, created = Watchlist.objects.update_or_create(
            user=user, movie_id=movie_id, defaults={"deleted_at": None}
        )
        return item

    def delete(self, watchlist: Watchlist) -> Watchlist:
        watchlist.deleted_at = timezone.now()
        watchlist.save()
        return watchlist
