from rest_framework import serializers
from .models import Watchlist


class WatchlistSerializer(serializers.ModelSerializer):
    movie_title = serializers.ReadOnlyField(source='movie.title')

    class Meta:
        model = Watchlist
        fields = ['id', 'movie', 'movie_title', 'added_at']
    
    def validate(self, data):
        user = self.context['request'].user
        movie = data.get('movie')

        if Watchlist.objects.filter(user=user, movie=movie).exists():
            raise serializers.ValidationError("Фильм уже был добавлен.")
        
        return data
