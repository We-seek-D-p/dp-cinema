"""Serializers for the movies application."""

from rest_framework import serializers
from .models import Genre, Movie


class GenreSerializer(serializers.ModelSerializer):
    """genre serializer (ReadOnly)"""

    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'name', 'slug']