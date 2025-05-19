from rest_framework import serializers
from offers_app.models import Offer, OfferDetails
from django.db.models import Min
from django.urls import reverse
from rest_framework.exceptions import ValidationError


class OfferDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for OfferDetails model providing full details.

    return:
        Serialized data of OfferDetails instance.
    """
    class Meta:
        model = OfferDetails
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']


class OfferDetailsGETSerializer(serializers.ModelSerializer):
    """
    Serializer for GET requests on OfferDetails.
    Returns only 'id' and a computed URL for the detail.

    return:
        Serialized data with id and url fields.
    """
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetails
        fields = ['id', 'url']

    def get_url(self, obj):
        """
        Compute URL for the OfferDetails instance, removing '/api' prefix.

        params:
            obj (OfferDetails): The OfferDetails instance.
        return:
            str: URL string for the OfferDetails.
        """
        url = reverse('offerdetails-detail', args=[obj.id])
        return url.replace('/api', '')  
    

class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for Offer model with nested OfferDetails.
    Supports custom create and update logic ensuring basic, standard, and premium details.

    return:
        Serialized Offer data including nested details and user info.
    raise:
        ValidationError: If 'details' data is missing required 'offer_type' or
                         does not include all required types ('basic', 'standard', 'premium').
    """
    details = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    image = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']
        extra_kwargs = {"user": {"read_only": True}}


    def to_representation(self, instance):
        """
        Dynamically modify representation to include user details on list action.

        params:
            instance (Offer): The Offer instance.
        return:
            dict: Serialized data with user details included conditionally.
        """
        data = super().to_representation(instance)
        request = self.context.get("request")
        
        view = self.context.get('view', None)
        if request and view and getattr(view, 'action', None) == "list":
            data["user_details"] = {
                "first_name": instance.user.first_name,
                "last_name": instance.user.last_name,
                "username": instance.user.username
            }
        else:
            data.pop("user_details", None)
        return data
    
    
    def validate(self, data):
        """
        Validates that the 'details' field in the input data includes all required offer types,
        but only for POST/PUT. PATCH is allowed to update single offer types.

        params:
            data (dict): The input data to validate.
        raise:
            ValidationError: If any detail is missing 'offer_type' or required types (on full update).
        return:
            dict: The validated data unchanged.
        """
        request = self.context.get("request")
        details_data = self.initial_data.get('details', [])

        if not details_data:
            return data

        for detail in details_data:
            if "offer_type" not in detail:
                raise ValidationError({"details": "Each offer detail must include an 'offer_type' field."})

        if request.method in ["POST", "PUT"]:
            required_types = {"basic", "standard", "premium"}
            existing_types = {detail.get("offer_type") for detail in details_data}
            if not required_types.issubset(existing_types):
                raise ValidationError({
                    "details": "Offers must include 'basic', 'standard', and 'premium' offer types."
                })

        return data


    def create(self, validated_data):
        """
        Create Offer instance ensuring 'basic', 'standard', and 'premium' details exist.

        params:
            validated_data (dict): Validated data from the request.
        return:
            Offer: Created Offer instance.
        raise:
            ValidationError: If offer details are missing 'offer_type' or required types.
        """
        details_data = self.initial_data.get('details', [])  
        user = self.context["request"].user  
        validated_data["user"] = user  

        offer = Offer.objects.create(**validated_data)

        offer_details = [OfferDetails(offer=offer, **detail_data) for detail_data in details_data]
        OfferDetails.objects.bulk_create(offer_details)

        return offer


    def update(self, instance, validated_data):
        """
        Update Offer instance and optionally its OfferDetails.

        params:
            instance (Offer): Offer instance to update.
            validated_data (dict): Validated data from the request.
        return:
            Offer: Updated Offer instance.
        """
        details_data = self.initial_data.get('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

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
                    OfferDetails.objects.create(offer=instance, **detail_data)

        return instance
    
    
    def get_details(self, obj):
        """
        Provide different serializers for details depending on request method.

        params:
            obj (Offer): Offer instance.
        return:
            list: Serialized OfferDetails data (full or minimal based on request).
        """
        request = self.context.get("request")

        if request and request.method in ["POST", "PUT"]:
            return OfferDetailsSerializer(obj.offer_details.all(), many=True).data  

        return OfferDetailsGETSerializer(obj.offer_details.all(), many=True).data


    def get_user_details(self, obj):
        """
        Return the user's basic info related to the Offer.

        params:
            obj (Offer): Offer instance.
        return:
            dict: Dictionary with user's first name, last name, and username.
        """
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "username": obj.user.username
        }


    def get_min_price(self, obj):
        """
        Compute minimum price from related OfferDetails.

        params:
            obj (Offer): Offer instance.
        return:
            float: Minimum price or 0.00 if none available.
        """
        min_price = obj.offer_details.aggregate(min_price=Min('price'))['min_price']
        return float(min_price) if min_price is not None else 0.00


    def get_min_delivery_time(self, obj):
        """
        Compute minimum delivery time from related OfferDetails.

        params:
            obj (Offer): Offer instance.
        return:
            int: Minimum delivery time in days or 0 if none available.
        """
        min_time = obj.offer_details.aggregate(min_time=Min('delivery_time_in_days'))['min_time']
        return min_time if min_time is not None else 0
    
    
    def get_image(self, obj):
        """
        Return absolute URL for the offer image if present.

        params:
            obj (Offer): Offer instance.
        return:
            str or None: Absolute URL of the image or None if no image.
        """
        if obj.image:
             request = self.context.get('request')  
             return request.build_absolute_uri(obj.image.url)  
        return None