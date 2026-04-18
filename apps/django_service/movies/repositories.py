from django.utils import timezone

from django.db.models import QuerySet
from .models import Movie, Watchlist
from users.models import User


class MovieRepository:
    def get_published(self):
        return Movie.objects.filter(is_published=True, deleted_at__isnull=True)

    def get_by_id(self, movie_id: int) -> Movie:
        return self.get_published().filter(id=movie_id).first()


class WatchListRepository:
    def get_user_watchlist(self, user: User) -> QuerySet[Watchlist, Watchlist]:
        return Watchlist.objects.filter(user=user, deleted_at__isnull=True)

    def get_item(self, user: User, movie_id: int) -> Movie | None:
        return self.get_user_watchlist(user).filter(id=movie_id).first()

    def exists(self, user: User, movie_id: int) -> bool:
        return self.get_user_watchlist(user).filter(id=movie_id).exists()

    def create_or_restore(self, user: User, movie_id: int) -> Watchlist:
        item, created = Watchlist.objects.update_or_create(user=user, movie_id=movie_id, defaults={'deleted_at': None})
        return item

    def delete(self, watchlist_item: Movie) -> Movie:
        watchlist_item.deleted_at = timezone.now()
        watchlist_item.save()
        return watchlist_item
