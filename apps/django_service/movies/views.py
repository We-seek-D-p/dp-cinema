from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from .models import Genre
from .repositories import MovieRepository
from .services import WatchListService
from .serializers import (
    WatchlistSerializer,
    WatchlistCreateSerializer, GenreSerializer,
)


class WatchlistPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class WatchListController(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = WatchlistPagination
    service = WatchListService()

    def get(self, request) -> Response:
        queryset = self.service.get_user_watchlist(request.user)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = WatchlistSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = WatchlistSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request) -> Response:
        serializer = WatchlistCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        watchlist = self.service.add_to_watchlist(request.user, serializer.validated_data["movie_id"])
        response_serializer = WatchlistSerializer(watchlist)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, movie_id) -> Response:
        self.service.remove_from_watchlist(user=request.user, movie_id=movie_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
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

    movie_repo = MovieRepository()

    def get_queryset(self):
        return self.movie_repo.get_published()
