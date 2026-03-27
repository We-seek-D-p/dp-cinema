from rest_framework import serializers

from .models import Genre, Movie, Watchlist


class WatchlistSerializer(serializers.ModelSerializer):
    movie_title = serializers.ReadOnlyField(source="movie.title")

    class Meta:
        model = Watchlist
        fields = ["id", "movie", "movie_title", "added_at"]

    def validate(self, data):
        user = self.context["request"].user
        movie = data.get("movie")

        if Watchlist.objects.filter(user=user, movie=movie).exists():
            raise serializers.ValidationError("Фильм уже был добавлен.")

        return data


class GenreSerializer(serializers.ModelSerializer):
    """genre serializer (ReadOnly)"""

    class Meta:
        model = Genre
        fields = ["id", "name", "slug"]
        read_only_fields = ["id", "name", "slug"]


class MovieListSerializer(serializers.ModelSerializer):
    """Compact movie serializer for list view"""

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "poster_url",
            "release_date",
            "is_premium",
            "is_published",
        ]
        read_only_fields = fields


class MovieDetailSerializer(serializers.ModelSerializer):
    """Detailed movie serializer with nested genres"""

    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = [
            "id",
            "title",
            "description",
            "poster_url",
            "hls_url",
            "release_date",
            "is_published",
            "is_premium",
            "genres",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
