from rest_framework import viewsets, permissions
from apps.offers.models import Offer
from .serializers import OfferSerializer

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)