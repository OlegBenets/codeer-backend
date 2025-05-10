from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.orders.models import Order
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]  # Alle Endpunkte erfordern Authentifizierung

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            models.Q(customer_user=user) | models.Q(business_user=user)
        )

    @action(detail=False, methods=['get'])
    def order_count(self, request, business_user_id=None):
        """Zählt die laufenden Bestellungen für einen bestimmten Geschäftsnutzer."""
        if business_user_id is not None:
            order_count = Order.objects.filter(business_user_id=business_user_id, status='in_progress').count()
            return Response({'order_count': order_count})
        return Response({'order_count': 0})

    @action(detail=False, methods=['get'])
    def completed_order_count(self, request, business_user_id=None):
        """Zählt die abgeschlossenen Bestellungen für einen bestimmten Geschäftsnutzer."""
        if business_user_id is not None:
            completed_order_count = Order.objects.filter(business_user_id=business_user_id, status='completed').count()
            return Response({'completed_order_count': completed_order_count})
        return Response({'completed_order_count': 0})

