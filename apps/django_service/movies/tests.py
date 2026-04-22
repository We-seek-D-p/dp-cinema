from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.django_service.movies.models import Genre, Movie, Watchlist


class MovieTests(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Comedy", slug="comedy")
        self.movie = Movie.objects.create(
            title="Valid film",
            description="Valid description.",
            is_published=True
        )
        self.movie.genres.add(self.genre)

    def test_movie_values(self):
        self.assertEqual(str(self.movie), "Valid film")
        self.assertEqual(self.movie.genres.first().name, "Comedy")


class WatchlistServiceTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tst_user",
            email="tst@test.com",
            password="password!123",
            is_premium=False
        )
        self.premium_user = User.objects.create_user(
            username="premium_user",
            email="premium@test.com",
            password="password@123",
            is_premium=True
        )
        self.movie = Movie.objects.create(
            title="Watchlist movie", 
            is_published=True, 
            is_premium=False
        )
        self.premium_movie = Movie.objects.create(
            title="Premium film", 
            is_published=True, 
            is_premium=True
        )

    def test_watchlist_add(self):
        self.item = Watchlist.objects.create(user=self.user, movie=self.movie)
        self.assertEqual(str(self.item), f"{self.user} → {self.movie}")
        self.assertEqual(self.user.watchlist_items.count(), 1)
