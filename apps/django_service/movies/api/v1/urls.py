from django.urls import path
from rest_framework.routers import DefaultRouter

from movies.api.v1.views import (
    GenreViewSet,
    MovieViewSet,
    WatchListController
)

movies_router = DefaultRouter()
movies_router.register("genres", GenreViewSet, basename="genres")
movies_router.register("", MovieViewSet, basename="movies")

movie_urlpatterns = movies_router.urls

watchlist_patterns = [
    path("", WatchListController.as_view(), name="watchlist"),
    path("<int:movie_id>", WatchListController.as_view(), name="watchlist-item"),
]
