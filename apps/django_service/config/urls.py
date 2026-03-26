"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from apps.django_service.users.views import (
    UserAccountController,
    UserLoginController,
    UserProfileController,
    UserRecoveryController,
)
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

api_v1_patterns = [
    path("register/", UserAccountController.as_view(), name="register"),
    path("login/", UserLoginController.as_view(), name="login"),
    path("profile/<int:pk>/", UserProfileController.as_view(), name="profile"),
    path("restore/", UserRecoveryController.as_view(), name="restore"),
    path("", include(router.urls)),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((api_v1_patterns, "api"), namespace="v1")),
]
