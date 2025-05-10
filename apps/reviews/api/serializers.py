from rest_framework import serializers
from apps.reviews.models import Review

class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.ReadOnlyField(source='reviewer.username')

    class Meta:
        model = Review
        fields = ['id', 'offer', 'reviewer', 'rating', 'comment', 'created_at']