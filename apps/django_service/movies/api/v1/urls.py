from django.urls import path
from movies.api.v1.views import (
    GenreViewSet,
    MovieExistsController,
    MovieProcessingCallbackController,
    MovieViewSet,
    WatchListController,
)
from rest_framework.routers import DefaultRouter

movies_router = DefaultRouter()
movies_router.register("genres", GenreViewSet, basename="genres")
movies_router.register("", MovieViewSet, basename="movies")

movie_urlpatterns = movies_router.urls

movie_callback_urlpatterns = [
    path(
        "processing/callback/",
        MovieProcessingCallbackController.as_view(),
        name="movie-processing-callback",
    ),
    path(
        "<int:movie_id>/exists/", MovieExistsController.as_view(), name="movie-exists"
    ),
]

watchlist_urlpatterns = [
    path("", WatchListController.as_view(), name="watchlist"),
    path("<int:movie_id>/", WatchListController.as_view(), name="watchlist-item"),
]
