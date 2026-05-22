from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from movies.api.permissions import InternalTokenPermission
from reviews.api.v1.serializers import ReviewIncomingWebhookSerializer
from reviews.services import ReviewModerationService
from movies.errors import MovieNotFoundError


class ReviewModerationController(APIView):
    permission_classes = [InternalTokenPermission]
    service = ReviewModerationService()

    def post(self, request) -> Response:
        serializer = ReviewIncomingWebhookSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            review = self.service.handle_incoming_review(serializer.validated_data)
            return Response({"review_id": review.id}, status=status.HTTP_200_OK)
        except MovieNotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
