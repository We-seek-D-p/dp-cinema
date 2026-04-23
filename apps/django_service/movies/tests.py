from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.django_service.movies.models import Genre, Movie, Watchlist
from apps.django_service.movies.services import WatchListService
from django.db import IntegrityError
from apps.django_service.movies.errors import (
    MovieNotFoundError,
    AlreadyInWatchlistError,
    WatchlistItemNotFoundError,
    PremiumContentRestrictedError,
)


class MovieTests(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Comedy", slug="comedy")
        self.movie = Movie.objects.create(
            title="Valid film", description="Valid description.", is_published=True
        )
        self.movie.genres.add(self.genre)

    def test_movie_values(self):
        self.assertEqual(str(self.movie), self.movie.title, "Valid film")
        self.assertEqual(self.movie.genres.first().name, "Comedy")

    def test_genre_unique(self):
        with self.assertRaises(IntegrityError):
            Genre.objects.create(name="other", slug="comedy")


class WatchlistServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="test_user",
            email="test@test.com",
            password="password!123",
            is_premium=False,
        )
        self.premium_user = User.objects.create_user(
            username="premium_user",
            email="premium@test.com",
            password="password@123",
            is_premium=True,
        )

        self.movie = Movie.objects.create(
            title="Basic movie", is_published=True, is_premium=False
        )
        self.premium_movie = Movie.objects.create(
            title="Premium movie", is_published=True, is_premium=True
        )

        self.service = WatchListService()

    def test_watchlist_add(self):
        added = self.service.add_to_watchlist(self.user, self.movie.id)
        item = Watchlist.objects.get(user=self.user, movie=self.movie)
        self.assertIsInstance(added, Watchlist)
        self.assertIsNone(item.deleted_at)
        self.assertEqual(self.user.watchlist_items.count(), 1)

    def test_watchlist_remove(self):
        self.service.add_to_watchlist(self.user, self.movie.id)
        self.service.remove_from_watchlist(self.user, self.movie.id)
        item = Watchlist.objects.get(user=self.user, movie=self.movie)
        self.assertIsNotNone(item.deleted_at)
        active_watchlist = self.service.get_user_watchlist(self.user)
        self.assertEqual(active_watchlist.count(), 0)

    def test_watchlist_unique(self):
        self.service.add_to_watchlist(self.user, self.movie.id)
        with self.assertRaises(AlreadyInWatchlistError):
            self.service.add_to_watchlist(self.user, self.movie.id)

    def test_movie_not_found(self):
        invalid_ids = (999999, -1)
        for id in invalid_ids:
            with self.assertRaises(MovieNotFoundError):
                self.service.add_to_watchlist(self.user, id)

    def test_watchlist_not_found(self):
        with self.assertRaises(WatchlistItemNotFoundError):
            self.service.remove_from_watchlist(self.user, self.movie.id)


class PremiumTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="test_user",
            email="test@test.com",
            password="password!123",
            is_premium=False
        )
        self.premium_user = User.objects.create_user(
            username="premium_user",
            email="premium@test.com",
            password="password@123",
            is_premium=True
        )
        self.premium_movie = Movie.objects.create(
            title="Premium movie",
            is_published=True, 
            is_premium=True
        )
        self.service = WatchListService()

    def test_premium_access(self):
        item = self.service.add_to_watchlist(self.premium_user, self.premium_movie.id)
        self.assertEqual(item.movie, self.premium_movie)

    def test_premium_error(self):
        with self.assertRaises(PremiumContentRestrictedError):
            self.service.add_to_watchlist(self.user, self.premium_movie.id)
