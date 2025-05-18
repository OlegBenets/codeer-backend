from rest_framework import viewsets, filters, status, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from orders_app.models import Order
from .serializers import OrderSerializer, CreateOrderSerializer, UpdateOrderStatusSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCustomerOrAdmin
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders between customer and business users.
    """
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]


    def get_queryset(self):
        """
        Filter orders based on the authenticated user.

        return:
            QuerySet: Orders relevant to the current user.
        """
        return Order.objects.filter(
            Q(customer_user=self.request.user) | Q(business_user=self.request.user)  
        )
    
    
    def get_permissions(self):
        """
        Set permissions dynamically based on the action.

        return:
            list: List of permission instances.
        """
        if self.action in ['create']:
            return [IsCustomerOrAdmin()]
        return [permissions.IsAuthenticated()]  
    
    
    def get_serializer_class(self):
        """
        Select serializer class based on the action.

        return:
            Serializer: The appropriate serializer class.
        """
        if self.action == 'create':
            return CreateOrderSerializer
        if self.action == 'partial_update':  
            return UpdateOrderStatusSerializer
        return OrderSerializer
    
    
    def get_serializer(self, *args, **kwargs):
        """
        Override to inject context into the serializer.

        return:
            Serializer: Initialized serializer instance.
        """
        kwargs['context'] = self.get_serializer_context()
        return super().get_serializer(*args, **kwargs)


    def perform_create(self, serializer):
        """
        Validate and create a new order for a customer user only.

        params:
            serializer (Serializer): Serializer instance with validated data.
        raise:
            PermissionDenied: If user is not a customer.
        """
        user_profile = getattr(self.request.user, 'profile', None)
        if not user_profile or user_profile.type != 'customer':
            raise PermissionDenied("Only customers can create orders.")
        serializer.save()


    def create(self, request, *args, **kwargs):
        """
        Handle order creation with proper error and success response.

        params:
            request (HttpRequest): The incoming request.
        return:
            Response: Success or error response based on validation and saving.
        """
        if not request.user.is_authenticated:
            return Response({"detail": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                order = serializer.save()
                return Response(
                    serializer.to_representation(order), 
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
        
        
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update the status of an order.

        params:
            request (HttpRequest): The incoming request.
        return:
            Response: Updated order data or error response.
        raise:
            PermissionDenied: If the user is not a business user.
        """
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        
        order = self.get_object()
        if not order:
            return Response({"detail": "The specified order was not found."}, status=status.HTTP_404_NOT_FOUND)
        
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile or user_profile.type != 'business':
            return Response({"detail": "Only business users are allowed to update order status."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(order, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def handle_exception(self, exc):
        """
        Handle exceptions for the viewset.

        params:
            exc (Exception): The exception raised.
        return:
            Response: Error response with proper status code.
        """
        response = super().handle_exception(exc)
        if response is None:
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response
    
    
class OrderCountView(APIView):
    """
    API endpoint to get the count of 'in_progress' orders for a business user.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, business_user_id): 
        """
        Retrieve the number of active orders for a given business user.

        params:
            request (HttpRequest): The request object.
            business_user_id (int): ID of the business user.
        return:
            Response: JSON with order count.
        raise:
            Http404: If the business user is not found.
        """
        business_user = get_object_or_404(User, id=business_user_id)
        order_count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        return Response({"order_count": order_count}, status=status.HTTP_200_OK)
    
    
class CompletedOrderCountView(APIView):
    """
    API endpoint to get the count of 'completed' orders for a business user.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, business_user_id):
        """
        Retrieve the number of completed orders for a given business user.

        params:
            request (HttpRequest): The request object.
            business_user_id (int): ID of the business user.
        return:
            Response: JSON with completed order count.
        raise:
            Http404: If the business user is not found.
        """
        business_user = get_object_or_404(User, id=business_user_id)
        completed_order_count = Order.objects.filter(business_user=business_user, status='completed').count()
        return Response({"completed_order_count": completed_order_count}, status=status.HTTP_200_OK)