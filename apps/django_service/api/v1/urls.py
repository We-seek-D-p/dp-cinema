from django.urls import include, path
from movies.api.v1.urls import (
    movie_callback_urlpatterns,
    movie_urlpatterns,
    watchlist_urlpatterns,
)
from reviews.api.v1.views import ReviewModerationController

app_name = "v1"

urlpatterns = [
    path("users/", include("users.api.v1.urls")),
    path("movies/", include((movie_callback_urlpatterns, "movies-callback"))),
    path("movies/", include((movie_urlpatterns, "movies"))),
    path("watchlist/", include((watchlist_urlpatterns, "watchlist"))),
    path("reviews/moderation/", ReviewModerationController.as_view(), name="review-moderation"),
]
