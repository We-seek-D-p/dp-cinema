from rest_framework import serializers


class ReviewIncomingWebhookSerializer(serializers.Serializer):
    review_id = serializers.IntegerField(required=True)
    movie_id = serializers.IntegerField(required=True)
    text = serializers.CharField(required=True)
    rating = serializers.IntegerField(required=True, min_value=1, max_value=10)
    user_id = serializers.IntegerField(required=True)
