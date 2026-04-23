from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    UserCreateSerializer,
    UserLoginRequestSerializer,
    UserPublicSerializer,
    UserProfileUpdateSerializer,
    UserRecoveryRequestSerializer,
)
from .services import UserService


class UserAccountController(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAuthenticated()]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = UserService()
        user = service.register(serializer.validated_data)

        return Response(UserPublicSerializer(user).data, status=status.HTTP_201_CREATED)


class UserLoginController(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = UserService()
        result = service.authenticate_user(serializer.validated_data)

        return Response(
            {
                "tokens": {
                    "access": result["access"],
                    "refresh": result["refresh"],
                },
                "user": UserPublicSerializer(result["user"]).data,
            },
            status=status.HTTP_200_OK,
        )


class UserProfileController(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        service = UserService()
        user = service.get_profile(pk)
        return Response(UserPublicSerializer(user).data)

    def patch(self, request, pk):
        serializer = UserProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = UserService()
        user = service.update_profile(pk, serializer.validated_data, request.user)
        return Response(UserPublicSerializer(user).data)

    def delete(self, request, pk):
        service = UserService()
        service.deactivate_account(pk, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRecoveryController(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRecoveryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = UserService()
        user = service.recover_account(serializer.validated_data["email"])
        return Response(UserPublicSerializer(user).data)
