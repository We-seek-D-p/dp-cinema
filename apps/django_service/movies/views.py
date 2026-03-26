from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Genre
from .serializers import GenreSerializer


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    'ViewSet for genres (ReadOnly)'
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]