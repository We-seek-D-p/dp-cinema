from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Genre, Movie
from .serializers import GenreSerializer, MovieListSerializer, MovieDetailSerializer


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for genres (ReadOnly)"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for moves (ReadOnly)"""
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genres__slug']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'release_date', 'created_at']
    ordering = ['title']

    def get_queryset(self):
        """Return only published movies"""
        return Movie.objects.filter(is_published=True, deleted_at__isnull=True)

    def get_serializer_class(self):
        """Return different serializers for list and detail"""
        if self.action == 'retrieve':
            return MovieDetailSerializer
        return MovieListSerializer