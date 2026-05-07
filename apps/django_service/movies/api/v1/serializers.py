from movies.models import Genre, Movie, Watchlist
from rest_framework import serializers


class WatchlistCreateSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField(required=True)


class WatchlistSerializer(serializers.ModelSerializer):
    movie_title = serializers.ReadOnlyField(source="movie.title")
    movie_poster = serializers.ReadOnlyField(source="movie.poster_url")

    class Meta:
        model = Watchlist
        fields = ["id", "movie", "movie_title", "movie_poster", "added_at"]
        read_only_fields = fields


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


class MovieProcessRequestSerializer(serializers.Serializer):
    source_url = serializers.URLField(required=False)

