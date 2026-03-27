from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Genre, Movie, Watchlist
from .serializers import (
    GenreSerializer,
    MovieDetailSerializer,
    MovieListSerializer,
    WatchlistSerializer,
)


class WatchlistViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        watchlist = Watchlist.objects.filter(user=request.user)
        serializer = WatchlistSerializer(watchlist, many=True)
        return Response(serializer.data)

    def post(self, request):
        movie_id = request.data.get("movie")
        if Watchlist.objects.filter(user=request.user, movie_id=movie_id).exists():
            return Response(
                {"detail": "Фильм уже был добавлен."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = WatchlistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            movie_item = Watchlist.objects.get(pk=pk, user=request.user)
            movie_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Watchlist.DoesNotExist:
            return Response(
                {"detail": "Фильм отсутствует в списке."},
                status=status.HTTP_404_NOT_FOUND,
            )


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for genres (ReadOnly)"""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for moves (ReadOnly)"""

    permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["genres__slug"]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "release_date", "created_at"]
    ordering = ["title"]

    def get_queryset(self):
        """Return only published movies"""
        return Movie.objects.filter(is_published=True, deleted_at__isnull=True)

    def get_serializer_class(self):
        """Return different serializers for list and detail"""
        if self.action == "retrieve":
            return MovieDetailSerializer
        return MovieListSerializer
