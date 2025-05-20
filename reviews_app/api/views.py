from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from reviews_app.models import Review
from .serializers import ReviewSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCustomerOrAdmin, IsReviewerOrAdmin
from rest_framework import serializers


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating, retrieving, updating, and deleting reviews between customers and business users.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["business_user", "reviewer"]
    ordering_fields = ["rating", "updated_at"]

    def get_permissions(self):
        """
        Determine permission based on action.

        return:
            list: List of permission instances for the current action.
        """
        if self.action in ["create"]:
            return [IsCustomerOrAdmin()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsReviewerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def partial_update(self, request, *args, **kwargs):
        """
        Allow partial updates only for 'rating' and 'description' fields.

        params:
            request (HttpRequest): The request containing partial update data.
        return:
            Response: Updated review data or validation error.
        """
        allowed_fields = {"rating", "description"}
        mutable_data = request.data.copy()
        request._full_data = {key: value for key, value in mutable_data.items() if key in allowed_fields}
        return super().partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Create a new review, ensuring a user can only review a business once.

        params:
            serializer (Serializer): The validated serializer instance.
        raise:
            ValidationError: If the user has already reviewed the business.
        """
        business_user = serializer.validated_data["business_user"]
        if Review.objects.filter(reviewer=self.request.user, business_user=business_user).exists():
            raise serializers.ValidationError({"detail": "You have already submitted a review for this business user."})
        serializer.save(reviewer=self.request.user)

    def get_queryset(self):
        """
        Filter the queryset based on optional query parameters.

        return:
            QuerySet: Filtered reviews based on business_user_id and reviewer_id.
        """
        queryset = super().get_queryset()
        business_user_id = self.request.query_params.get("business_user_id")
        reviewer_id = self.request.query_params.get("reviewer_id")

        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        return queryset
