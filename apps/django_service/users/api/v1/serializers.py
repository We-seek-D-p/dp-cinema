from rest_framework import serializers
from users.models import Subscription, User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password", "birth_date"]
        extra_kwargs = {"password": {"write_only": True}, "email": {"required": True}}


class UserLoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "avatar_url", "birth_date", "is_premium"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "avatar_url", "birth_date"]


class UserRecoveryRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class UserSubscriptionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "subscribed_at", "expires_at"]


class UserSubscriptionRequestSerializer(serializers.ModelSerializer):
    days = serializers.IntegerField(min_value=1, max_value=365, default=30)
