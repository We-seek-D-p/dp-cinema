import asyncio

from django_filters.rest_framework import DjangoFilterBackend
from movies.api.v1.serializers import (
    GenreSerializer,
    MovieDetailSerializer,
    MovieListSerializer,
    MovieProcessRequestSerializer,
    WatchlistCreateSerializer,
    WatchlistSerializer,
)
from movies.models import Genre
from movies.repositories import MovieRepository
from movies.services import MovieUploadService, WatchListService
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class WatchlistPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
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

        watchlist = self.service.add_to_watchlist(
            request.user, serializer.validated_data["movie_id"]
        )
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

    def get_serializer_class(self):
        if self.action == "list":
            return MovieListSerializer
        if self.action == "retrieve":
            return MovieDetailSerializer
        return MovieDetailSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def process_video(self, request, pk=None):
        serializer = MovieProcessRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_url = serializer.validated_data.get("source_url")

        service = MovieUploadService()

        try:
            result = asyncio.run(service.process_movie(
                movie_id=pk,
                input_url=input_url
            ))

            if "error" in result:
                return Response(result, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            return Response(result, status=status.HTTP_202_ACCEPTED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Internal server error", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MovieCallbackController(APIView):
    permission_classes = [AllowAny] # Костыль на время - надо использовать secret key для 2 сервисов

    def post(self, request):
        movie_id = request.data.get("movie_id")
        hls_url = request.data.get("hls_url")

        if not movie_id or not hls_url:
            return Response({"error": "Missing data"}, status=status.HTTP_400_BAD_REQUEST)

        service = MovieUploadService()
        result = service.finalize_processing(movie_id, hls_url)

        if not result:
            return Response({"error": "Movie not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"status": "success"}, status=200)

