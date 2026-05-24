from unittest.mock import patch
from django.conf import settings
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from movies.models import Movie 
from movies.errors import MovieNotFoundError
from reviews.models import Review, ReviewStatus
from reviews.services import ReviewModerationService, FlaskReviewsClient


class ReviewTests(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(title="A movie", is_published=True)
        self.review = Review.objects.create(
            id=1,
            movie=self.movie,
            user_id=4,
            text="abc",
            rating=9,
            status=ReviewStatus.PENDING,
        )

    def test_review_values(self):
        self.assertEqual(str(self.review), f"Review #1 → A movie (pending)")
        self.assertEqual(self.review.rating, 9)
        self.assertEqual(self.review.status, ReviewStatus.PENDING)


class ReviewModerationTests(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(title="second movie", is_published=True)
        self.service = ReviewModerationService()
        self.valid_data = {
            "review_id": 10,
            "movie_id": self.movie.id,
            "user_id": 5,
            "text": "acb",
            "rating": 1,
        }

    def test_incoming_review_success(self):
        review = self.service.handle_incoming_review(self.valid_data)
        self.assertIsInstance(review, Review)
        self.assertEqual(review.id, 10)
        self.assertEqual(review.status, ReviewStatus.PENDING)

    def test_incoming_review_movie_not_found(self):
        invalid_data = self.valid_data.copy()
        invalid_data["movie_id"] = 90909
        with self.assertRaises(MovieNotFoundError):
            self.service.handle_incoming_review(invalid_data)


class ReviewWebHookTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.movie = Movie.objects.create(title="third movie", is_published=True)
        self.url = "/api/v1/internal/reviews/moderation/"
        self.secret_token = "test_token"
        settings.INTERNAL_SERVICE_TOKEN = self.secret_token
        self.valid_payload = {
            "review_id": 2,
            "movie_id": self.movie.id,
            "user_id": 12,
            "text": "bac",
            "rating": 8,
        }

    def test_webhook_success(self):
        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
            HTTP_X_INTERNAL_TOKEN=self.secret_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"review_id": 2})

    def test_webhook_permission_denied(self):
        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
            HTTP_X_INTERNAL_TOKEN="wrong_token",
        )
        self.assertIn(response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_webhook_movie_not_found(self):
        payload = self.valid_payload.copy()
        payload["movie_id"] = 89999
        
        response = self.client.post(
            self.url,
            payload,
            format="json",
            HTTP_X_INTERNAL_TOKEN=self.secret_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_webhook_invalid_payload(self):
        invalid_payload = {"review_id": 2, "movie_id": self.movie.id}
        response = self.client.post(
            self.url,
            invalid_payload,
            format="json",
            HTTP_X_INTERNAL_TOKEN=self.secret_token,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FlaskReviewsTests(TestCase):
    @patch("reviews.services.httpx.Client.patch")
    def test_send_status_update(self, mock_patch):
        mock_patch.return_value.status_code = 200
        result = FlaskReviewsClient.send_status_update(review_id=1, status="approved")
        self.assertTrue(result)

    @patch("reviews.services.httpx.Client.patch")
    def test_send_status_update_fail(self, mock_patch):
        mock_patch.return_value.status_code = 400
        result = FlaskReviewsClient.send_status_update(review_id=1, status="approved")
        self.assertFalse(result)
