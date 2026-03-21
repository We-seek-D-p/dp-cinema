from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    UserCreateSerializer,
    UserLoginRequestSerializer,
    UserPublicSerializer,
)
from .services import UserService


class UserAccountController(APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = UserService().register(serializer.validated_data)
            return Response(UserPublicSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginController(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginRequestSerializer(data=request.data)

        if serializer.is_valid():
            service = UserService()
            result = service.authenticate_user(serializer.validated_data)

            if result:
                return Response({
                    "tokens": {
                        "access": result['access'],
                        "refresh": result['refresh']
                    },
                    "user": UserPublicSerializer(result['user']).data
                }, status=status.HTTP_200_OK)

            return Response({"detail": "Неверный логин или пароль"}, status=401)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileController(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = UserService().get_profile(pk)
        if not user:
            return Response({"detail": "User not found or deactivated"}, status=404)
        return Response(UserPublicSerializer(user).data)

    def patch(self, request, pk):
        if str(request.user.id) != str(pk):
            return Response({"detail": "Permission denied"}, status=403)

        user = UserService().update_profile(pk, request.data)
        return Response(UserPublicSerializer(user).data)

    def delete(self, request, pk):
        if str(request.user.id) != str(pk):
            return Response({"detail": "Permission denied"}, status=403)

        if UserService().deactivate_account(pk):
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=404)


class UserRecoveryController(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user = UserService().recover_account(email)
        if user:
            return Response(UserPublicSerializer(user).data)
        return Response({"detail": "Active user not found or nothing to recover"}, status=404)
