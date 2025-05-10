from rest_framework import serializers
from apps.offers.models import Offer

class OfferSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Offer
        fields = ['id', 'title', 'description', 'price', 'created_at', 'owner']