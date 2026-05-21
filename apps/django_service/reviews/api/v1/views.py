from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from movies.api.permissions import InternalTokenPermission
from reviews.api.v1.serializers import ReviewIncomingWebhookSerializer
from reviews.services import ReviewModerationService


class ReviewModerationController(APIView):
    permission_classes = [InternalTokenPermission]
    service = ReviewModerationService()

    def post(self, request) -> Response:
        serializer = ReviewIncomingWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.service.handle_incoming_review(serializer.validated_data)
            return Response(
                {"status": "success"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
