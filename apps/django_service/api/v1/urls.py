from django.urls import include, path

from movies.api.v1.urls import (
    movie_urlpatterns,
    watchlist_urlpatterns,
)

app_name = "v1"

urlpatterns = [
    path("users/", include("users.api.v1.urls")),
    path("movies/", include((movie_urlpatterns, "movies"))),
    path("watchlist/", include((watchlist_urlpatterns, "watchlist"))),
]
