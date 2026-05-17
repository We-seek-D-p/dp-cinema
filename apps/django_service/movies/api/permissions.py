from django.conf import settings
from django.utils.crypto import constant_time_compare
from rest_framework.permissions import BasePermission


class InternalTokenPermission(BasePermission):
    def has_permission(self, request, view):
        token = request.headers.get("X-Internal-Token")
        if not settings.INTERNAL_SERVICE_TOKEN or not token:
            return False
        return constant_time_compare(token, settings.INTERNAL_SERVICE_TOKEN)
