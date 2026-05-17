from django.db.models import QuerySet
from django.utils import timezone
from users.models import User

from .models import Movie, ProcessingStatus, Watchlist


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

    def mark_processing_queued(self, movie: Movie, source_url: str) -> Movie:
        movie.source_url = source_url
        movie.is_published = False
        movie.processing_status = ProcessingStatus.QUEUED
        movie.processing_task_id = ""
        movie.processing_error = ""
        movie.save(
            update_fields=[
                "source_url",
                "is_published",
                "processing_status",
                "processing_task_id",
                "processing_error",
                "updated_at",
            ]
        )
        return movie

    def save_processing_task_id(self, movie: Movie, task_id: str) -> Movie:
        movie.processing_task_id = task_id
        movie.save(update_fields=["processing_task_id", "updated_at"])
        return movie

    def mark_processing_failed(self, movie: Movie, error_text: str) -> Movie:
        movie.processing_status = ProcessingStatus.FAILED
        movie.processing_error = error_text
        movie.save(
            update_fields=["processing_status", "processing_error", "updated_at"]
        )
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
