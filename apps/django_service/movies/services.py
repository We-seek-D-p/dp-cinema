import httpx
from django.conf import settings
from django.db.models import QuerySet
from users.models import User

from .errors import (
    AlreadyInWatchlistError,
    MovieNotFoundError,
    PremiumContentRestrictedError,
    WatchlistItemNotFoundError,
)
from .models import Watchlist
from .repositories import MovieRepository, WatchListRepository


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


class MovieUploadService:
    def __init__(self):
        self.movie_repo = MovieRepository()
        self.fastapi_url = settings.FASTAPI_SERVICE_URL

    async def process_movie(self, movie_id: int, input_url: str | None) -> dict:
        movie = self.movie_repo.get_by_id_internal(movie_id)
        if not movie:
            raise MovieNotFoundError()

        source_url = input_url or movie.source_url
        if not source_url:
            raise ValueError("No source URL provided")

        self.movie_repo.mark_processing_queued(movie, source_url)

        try:
            result = await self._send_to_fastapi(movie_id, source_url)
        except httpx.HTTPError as err:
            self.movie_repo.mark_processing_failed(movie, str(err))
            return {"error": "FastAPI service is down", "details": str(err)}

        task_id = result.get("task_id")
        if task_id:
            self.movie_repo.save_processing_task_id(movie, str(task_id))
        return result

    async def _send_to_fastapi(self, movie_id: int, source_url: str) -> dict:
        payload = {"movie_id": movie_id, "source_url": source_url}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.fastapi_url}/api/v1/movies/process/",
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    def finalize_processing(self, movie_id: int, hls_url: str):
        movie = self.movie_repo.get_by_id_internal(movie_id)
        if not movie:
            return None

        return self.movie_repo.finalize_movie(movie, hls_url)
