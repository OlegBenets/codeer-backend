from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from offers_app.models import Offer, OfferDetails
from .serializers import OfferSerializer, OfferDetailsSerializer
from rest_framework.permissions import AllowAny
from .pagination import CustomPageNumberPagination  
from django.shortcuts import get_object_or_404
from django.db.models import Min
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from rest_framework.exceptions import ValidationError


class OfferViewset(viewsets.ModelViewSet):
    """
    A viewset for managing business user offers.
    """
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    permission_classes = [AllowAny]
    pagination_class = CustomPageNumberPagination

    filterset_fields = {
        'user': ['exact'], 
        'updated_at': ['gte'],
        'offer_details__price': ['gte'],  
        'offer_details__delivery_time_in_days': ['exact', 'lte', 'gte']
    }
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at']


    def get_queryset(self):
        """
        Optionally filters offers by creator_id, min_price, or max_delivery_time.

        query_params:
            creator_id (int): Filter by user ID
            max_delivery_time (int): Maximum allowed delivery time (in days)
            min_price (float): Minimum price filter
        return: 
            QuerySet of filtered Offer instances
        raise:
            ValidationError: If max_delivery_time or min_price is not numeric
        """
        queryset = Offer.objects.annotate(
            min_price=Min('offer_details__price')
        )
        creator_id = self.request.query_params.get('creator_id')
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        min_price = self.request.query_params.get('min_price')

        if creator_id:
            queryset = queryset.filter(user_id=creator_id)

        if max_delivery_time:
            try:
                max_delivery_time = int(max_delivery_time)
            except ValueError:
                raise ValidationError({"error": "max_delivery_time must be an integer."})
            queryset = queryset.filter(offer_details__delivery_time_in_days__lte=max_delivery_time)

        if min_price:
            try:
                min_price = float(min_price)
            except ValueError:
                raise ValidationError({"error": "min_price must be a number."})
            queryset = queryset.filter(min_price__gte=min_price)

        return queryset
    
    
    def update(self, request, *args, **kwargs):
        """
        Update an offer and its details, validating permissions and user role.

        param:
            request (Request): The HTTP request
            kwargs (dict): Should include 'pk' of the Offer
        return:
            Response: Updated offer data
        raise:
            AuthenticationFailed: If the user is not logged in
            PermissionDenied: If user is not the offer owner or not a business
            ValidationError: If a non-existing offer_type is updated
        """
        if not request.user.is_authenticated:
            raise AuthenticationFailed({"detail": "Authentication required."})

        instance = get_object_or_404(Offer, pk=kwargs.get("pk"))  

        if instance.user != request.user:
            raise PermissionDenied({"detail": "You do not have permission to edit this offer."})

        user_profile = getattr(request.user, "profile", None)
        if not user_profile or user_profile.type != "business":
            raise PermissionDenied({"detail": "Only business users may edit their offers."})

        details_data = request.data.get('details', [])

        if details_data is not None:
            existing_details = {detail.offer_type: detail for detail in instance.offer_details.all()}
            for detail_data in details_data:
                offer_type = detail_data.get("offer_type")
                if offer_type in existing_details:
                    detail_instance = existing_details[offer_type]
                    for attr, value in detail_data.items():
                        setattr(detail_instance, attr, value)
                    detail_instance.save()
                else:
                    raise ValidationError({"detail": f"Offer type '{offer_type}' does not exist for this offer."})

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        updated_instance = self.get_queryset().get(pk=instance.pk)
        response_serializer = self.get_serializer(updated_instance)

        return Response(response_serializer.data, status=status.HTTP_200_OK)


    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific offer by ID.

        raise:
            AuthenticationFailed: If the user is not logged in
        """
        if not self.request.user.is_authenticated:
            raise AuthenticationFailed({"detail": "Authentication required."})
        instance = get_object_or_404(Offer, pk=kwargs.get("pk"))
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def perform_create(self, serializer):
        """
        Save a new offer, ensuring only business users can create.

        raise:
            AuthenticationFailed: If the user is not authenticated
            PermissionDenied: If user is not a business
        """
        if not self.request.user.is_authenticated:
            raise AuthenticationFailed({"detail": "Authentication required."})
        user_profile = getattr(self.request.user, "profile", None)
        if not user_profile or user_profile.type != "business":
            raise PermissionDenied({"detail": "Only business users may create offers."})
        serializer.save(user=self.request.user)


    def perform_update(self, serializer):
        """
        Save offer update, ensuring only the owner can update.

        raise:
            AuthenticationFailed, PermissionDenied
        """
        instance = self.get_object()
        if not self.request.user.is_authenticated:
            raise AuthenticationFailed({"detail": "Authentication required."}) 
        if instance.user != self.request.user:
            raise PermissionDenied({"detail": "You do not have permission to edit this offer."})
        user_profile = getattr(self.request.user, "profile", None)
        if not user_profile or user_profile.type != "business":
            raise PermissionDenied({"detail": "Only business users may edit their offers."})
        serializer.save()


    def handle_exception(self, exc):
        """
        Custom exception handler for internal server errors.
        """
        response = super().handle_exception(exc)
        if response is None:
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response
        
        
    def destroy(self, request, *args, **kwargs):
        """
        Delete an offer.

        raise:
            AuthenticationFailed: If the user is not logged in
            PermissionDenied: If the user is a customer
        """
        if not request.user.is_authenticated:
            raise AuthenticationFailed("You must be logged in to perform this action.")  

        user_profile = getattr(self.request.user, "profile", None)
        if not user_profile or user_profile.type == 'customer':
            raise PermissionDenied("Customers are not allowed to delete offers.") 
        
        instance = get_object_or_404(Offer, pk=kwargs.get("pk"))  

        return super().destroy(request, *args, **kwargs)


class OfferDetailsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for retrieving offer detail entries.
    """
    queryset = OfferDetails.objects.all()
    serializer_class = OfferDetailsSerializer


    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific offer detail by ID.

        params:
            request (HttpRequest): The request object.
        return:
            Response: Offer detail data or error response.
        raise:
            Http404: If the offer detail does not exist.
            PermissionDenied: If the user is not authenticated.
        """
        if not request.user.is_authenticated:
            return Response({"detail": "User is not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)
        pk = kwargs.get("pk")
        if pk is None or not str(pk).isdigit():  
            return Response({"detail": "Invalid or missing ID."}, status=status.HTTP_400_BAD_REQUEST)
        offer_detail = get_object_or_404(OfferDetails, pk=kwargs.get("pk"))
        serializer = self.get_serializer(offer_detail)
        return Response(serializer.data, status=status.HTTP_200_OK) 


    def handle_exception(self, exc):
        """
        Handle unexpected exceptions during view execution.

        params:
            exc (Exception): The raised exception.
        return:
            Response: Standardized error response.
        """
        response = super().handle_exception(exc)
        if response is None:
            return Response({"detail": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        return response