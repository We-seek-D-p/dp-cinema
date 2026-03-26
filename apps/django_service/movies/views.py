from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Watchlist
from .serializers import WatchlistSerializer


class WatchlistViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        watchlist = Watchlist.objects.filter(user=request.user)
        serializer = WatchlistSerializer(watchlist, many=True)
        return Response(serializer.data)

    def post(self, request):
        movie_id = request.data.get('movie')
        if Watchlist.objects.filter(user=request.user, movie_id=movie_id).exists():
            return Response(
                {"detail": "Фильм уже был добавлен."},
                status=status.HTTP_400_BAD_REQUEST
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
                {"detail": "Фильм отстутствует в списке."}, 
                status=status.HTTP_404_NOT_FOUND
            )
