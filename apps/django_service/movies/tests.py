from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from movies.errors import (
    AlreadyInWatchlistError,
    MovieNotFoundError,
    PremiumContentRestrictedError,
    WatchlistItemNotFoundError,
)
from movies.models import Genre, Movie, Watchlist
from movies.services import WatchListService
from rest_framework.test import APITestCase

STANDARD_PASSWORD = "password!123"  # noqa: S105
PREMIUM_PASSWORD = "password@123"  # noqa: S105


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
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="test_user",
            email="test@test.com",
            password=STANDARD_PASSWORD,
            is_premium=False,
        )
        self.premium_user = user_model.objects.create_user(
            username="premium_user",
            email="premium@test.com",
            password=PREMIUM_PASSWORD,
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
        for movie_id in invalid_ids:
            with self.assertRaises(MovieNotFoundError):
                self.service.add_to_watchlist(self.user, movie_id)

    def test_watchlist_not_found(self):
        with self.assertRaises(WatchlistItemNotFoundError):
            self.service.remove_from_watchlist(self.user, self.movie.id)

    def test_watchlist_remove_deleted(self):
        self.service.add_to_watchlist(self.user, self.movie.id)
        self.service.remove_from_watchlist(self.user, self.movie.id)
        with self.assertRaises(WatchlistItemNotFoundError):
            self.service.remove_from_watchlist(self.user, self.movie.id)


class PremiumTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="test_user",
            email="test@test.com",
            password=STANDARD_PASSWORD,
            is_premium=False,
        )
        self.premium_user = user_model.objects.create_user(
            username="premium_user",
            email="premium@test.com",
            password=PREMIUM_PASSWORD,
            is_premium=True,
        )
        self.premium_movie = Movie.objects.create(
            title="Premium movie", is_published=True, is_premium=True
        )
        self.service = WatchListService()

    def test_premium_access(self):
        item = self.service.add_to_watchlist(self.premium_user, self.premium_movie.id)
        self.assertEqual(item.movie, self.premium_movie)

    def test_premium_error(self):
        with self.assertRaises(PremiumContentRestrictedError):
            self.service.add_to_watchlist(self.user, self.premium_movie.id)

    def test_premium_upgrade(self):
        self.user.is_premium = True
        self.user.save()
        item = self.service.add_to_watchlist(self.user, self.premium_movie.id)
        self.assertEqual(item.movie, self.premium_movie)

    def test_premium_downgrade(self):
        self.premium_user.is_premium = False
        self.premium_user.save()
        with self.assertRaises(PremiumContentRestrictedError):
            self.service.add_to_watchlist(self.premium_user, self.premium_movie.id)


class MovieApiSerializerSelectionTests(APITestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Action", slug="action")
        self.movie = Movie.objects.create(
            title="Movie",
            description="Description",
            poster_url="https://example.com/poster.jpg",
            hls_url="https://example.com/stream.m3u8",
            is_published=True,
            is_premium=False,
        )
        self.movie.genres.add(self.genre)

    def test_movies_list_uses_compact_structure(self):
        response = self.client.get("/api/v1/movies/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)

        movie_data = response.data["results"][0]

        self.assertEqual(movie_data["id"], self.movie.id)
        self.assertEqual(
            set(movie_data.keys()),
            {
                "id",
                "title",
                "poster_url",
                "release_date",
                "is_premium",
                "is_published",
            },
        )
        self.assertNotIn("description", movie_data)
        self.assertNotIn("genres", movie_data)

    def test_movies_detail_uses_full_structure(self):
        response = self.client.get(f"/api/v1/movies/{self.movie.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.movie.id)
        self.assertEqual(response.data["description"], self.movie.description)
        self.assertIn("hls_url", response.data)
        self.assertIn("genres", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)
        self.assertNotIn("results", response.data)

        self.assertEqual(len(response.data["genres"]), 1)
        self.assertEqual(
            set(response.data["genres"][0].keys()),
            {"id", "name", "slug"},
        )


class MovieApiListBehaviorTests(APITestCase):
    def setUp(self):
        self.action = Genre.objects.create(name="Action", slug="action")
        self.comedy = Genre.objects.create(name="Comedy", slug="comedy")

        now = timezone.now()

        for index in range(25):
            movie = Movie.objects.create(
                title=f"Movie {index:02d}",
                description=f"Story line {index}",
                release_date=now.date() - timedelta(days=index),
                is_published=True,
            )
            movie.genres.add(self.action if index % 2 else self.comedy)
            Movie.objects.filter(id=movie.id).update(
                created_at=now - timedelta(hours=index)
            )

        self.title_match = Movie.objects.create(
            title="Unique Alpha Title",
            description="Generic description",
            release_date=now.date(),
            is_published=True,
        )
        self.title_match.genres.add(self.action)
        Movie.objects.filter(id=self.title_match.id).update(
            created_at=now + timedelta(minutes=1)
        )

        self.description_match = Movie.objects.create(
            title="Regular title",
            description="Hidden needle phrase",
            release_date=now.date() - timedelta(days=60),
            is_published=True,
        )
        self.description_match.genres.add(self.comedy)
        Movie.objects.filter(id=self.description_match.id).update(
            created_at=now + timedelta(minutes=2)
        )

        self.total_movies = Movie.objects.filter(
            is_published=True,
            deleted_at__isnull=True,
        ).count()

    def _movie_ids(self, response):
        return [item["id"] for item in response.data["results"]]

    def _published_movies(self):
        return Movie.objects.filter(
            is_published=True,
            deleted_at__isnull=True,
        )

    def test_movies_list_default_pagination_shape(self):
        response = self.client.get("/api/v1/movies/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

        self.assertEqual(response.data["count"], self.total_movies)
        self.assertEqual(len(response.data["results"]), 20)
        self.assertIsNone(response.data["previous"])
        self.assertIsNotNone(response.data["next"])

    def test_movies_list_page_query_param(self):
        response = self.client.get("/api/v1/movies/?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], self.total_movies)
        self.assertIsNotNone(response.data["previous"])
        self.assertIsNone(response.data["next"])
        self.assertEqual(len(response.data["results"]), 7)

    def test_movies_list_invalid_page_values(self):
        for invalid_page in ["0", "abc", "9999"]:
            response = self.client.get(f"/api/v1/movies/?page={invalid_page}")

            self.assertEqual(response.status_code, 404)
            self.assertIn("detail", response.data)

    def test_movies_list_page_size_is_ignored(self):
        for page_size in ["5", "999", "invalid"]:
            response = self.client.get(f"/api/v1/movies/?page_size={page_size}")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data["results"]), 20)

    def test_movies_list_filter_by_genre_slug(self):
        response = self.client.get("/api/v1/movies/?genres__slug=action")

        expected_ids = list(
            self._published_movies()
            .filter(genres__slug="action")
            .order_by("title")
            .values_list("id", flat=True)[:20]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._movie_ids(response), expected_ids)

    def test_movies_list_filter_by_unknown_genre_slug_returns_empty_result(self):
        response = self.client.get("/api/v1/movies/?genres__slug=missing")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_movies_list_search_by_title(self):
        response = self.client.get("/api/v1/movies/?search=Unique%20Alpha")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(self._movie_ids(response), [self.title_match.id])

    def test_movies_list_search_by_description(self):
        response = self.client.get("/api/v1/movies/?search=needle")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(self._movie_ids(response), [self.description_match.id])

    def test_movies_list_ordering_title(self):
        response = self.client.get("/api/v1/movies/?ordering=title")

        expected_ids = list(
            self._published_movies()
            .order_by("title")
            .values_list("id", flat=True)[:20]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._movie_ids(response), expected_ids)

    def test_movies_list_ordering_release_date(self):
        response = self.client.get("/api/v1/movies/?ordering=release_date")

        expected_ids = list(
            self._published_movies()
            .order_by("release_date")
            .values_list("id", flat=True)[:20]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._movie_ids(response), expected_ids)

    def test_movies_list_ordering_created_at(self):
        response = self.client.get("/api/v1/movies/?ordering=created_at")

        expected_ids = list(
            self._published_movies()
            .order_by("created_at")
            .values_list("id", flat=True)[:20]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._movie_ids(response), expected_ids)

    def test_movies_list_invalid_ordering_falls_back_to_default(self):
        response = self.client.get("/api/v1/movies/?ordering=unknown_field")

        expected_ids = list(
            self._published_movies()
            .order_by("title")
            .values_list("id", flat=True)[:20]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._movie_ids(response), expected_ids)
