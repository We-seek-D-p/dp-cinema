from django.conf import settings
from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    source_url = models.URLField(max_length=500, blank=True)
    poster_url = models.URLField(max_length=500, blank=True)
    hls_url = models.URLField(max_length=500, blank=True)
    release_date = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    genres = models.ManyToManyField(Genre, related_name="movies", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["is_published"], name="movie_is_published_idx"),
        ]

    def __str__(self) -> str:
        return self.title


class Watchlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="watchlist_items",
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="watchlisted_by",
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-added_at"]
        unique_together = ("user", "movie")

    def __str__(self) -> str:
        return f"{self.user} → {self.movie}"
