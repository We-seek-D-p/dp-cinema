from django.db import models
from movies.models import Movie


class ReviewStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    HIDDEN = "hidden", "Hidden"


class Review(models.Model):
    id = models.IntegerField(primary_key=True, verbose_name="Review ID")
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user_id = models.IntegerField(verbose_name="User ID")
    text = models.TextField()
    rating = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def __str__(self) -> str:
        return f"Review #{self.id} → {self.movie.title} ({self.status})"
