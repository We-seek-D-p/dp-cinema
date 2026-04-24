from django.urls import path

from users.api.v1.views import (
    UserAccountController,
    UserLoginController,
    UserProfileController,
    UserRecoveryController,
)

urlpatterns = [
    path("register/", UserAccountController.as_view(), name="register"),
    path("login/", UserLoginController.as_view(), name="login"),
    path("profile/<int:pk>/", UserProfileController.as_view(), name="profile"),
    path("restore/", UserRecoveryController.as_view(), name="restore"),
]
