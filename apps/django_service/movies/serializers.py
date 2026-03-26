"""Serializers for the movies application."""
from re import match

from rest_framework import serializers
from .models import Genre, Movie


class GenreSerializer(serializers.ModelSerializer):
    """genre serializer (ReadOnly)"""

    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'name', 'slug']


class MovieListSerializer(serializers.ModelSerializer):
    """Compact movie serializer for list view"""

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'poster_url', 'release_date',
            'is_premium', 'is_published'
        ]
        read_only_fields = fields


class MovieDetailSerializer(serializers.ModelSerializer):
    """Detailed movie serializer with nested genres"""

    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        match = Movie
        fields = [
            'id', 'title', 'description', 'poster_url', 'hls_url',
            'release_date', 'is_published', 'is_premium', 'genres',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields