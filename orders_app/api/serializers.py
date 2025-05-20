from rest_framework import serializers
from orders_app.models import Order
from offers_app.models import OfferDetails


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model providing read-only access to related user and offer fields.

    return:
        Serialized Order data.
    """

    customer_user = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(read_only=True)
    title = serializers.CharField(read_only=True)
    revisions = serializers.IntegerField(read_only=True)
    delivery_time_in_days = serializers.IntegerField(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    features = serializers.JSONField(read_only=True)
    offer_type = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class CreateOrderSerializer(serializers.Serializer):
    """
    Serializer to create an Order from an offer detail ID.

    params:
        offer_detail_id (int): The ID of the OfferDetails to create the order from.
    return:
        Order: Created Order instance.
    raise:
        OfferDetails.DoesNotExist: If the offer_detail_id does not exist.
    """

    offer_detail_id = serializers.IntegerField()

    def create(self, validated_data):
        """
        Create an Order instance linked to the provided OfferDetails.

        params:
            validated_data (dict): Data validated by serializer.
        return:
            Order: Created Order instance.
        raise:
            OfferDetails.DoesNotExist: If offer_detail_id is invalid.
        """
        offer_detail = OfferDetails.objects.get(id=validated_data["offer_detail_id"])
        offer = offer_detail.offer

        customer_user = self.context["request"].user
        business_user = offer.user

        order = Order(
            customer_user=customer_user,
            business_user=business_user,
            offer_detail=offer_detail,
            title=offer.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status="in_progress",
        )
        order.save(force_insert=True)

        return order

    def to_representation(self, instance):
        """
        Serialize the created Order instance without nested offer_detail.

        params:
            instance (Order): The created Order instance.
        return:
            dict: Serialized Order data without offer_detail.
        """
        data = {
            "id": instance.id,
            "customer_user": instance.customer_user.id,
            "business_user": instance.business_user.id,
            "title": instance.title,
            "revisions": instance.revisions,
            "delivery_time_in_days": instance.delivery_time_in_days,
            "price": instance.price,
            "features": instance.features,
            "offer_type": instance.offer_type,
            "status": instance.status,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }
        return data


class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    """
    Serializer to update only the status field of an Order.

    return:
        Updated Order instance.
    raise:
        serializers.ValidationError: If status value is invalid.
    """

    class Meta:
        model = Order
        fields = ["status"]

    def validate_status(self, value):
        """
        Validate that the status is one of allowed choices.

        params:
            value (str): Status string to validate.
        return:
            str: Validated status value.
        raise:
            serializers.ValidationError: If status is invalid.
        """
        valid_statuses = ["in_progress", "completed", "cancelled"]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Allowed values are: {', '.join(valid_statuses)}")
        return value

    def update(self, instance, validated_data):
        """
        Update the status field of the Order.

        params:
            instance (Order): Order instance to update.
            validated_data (dict): Data validated by serializer.
        return:
            Order: Updated Order instance.
        """
        instance.status = validated_data.get("status", instance.status)
        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Serialize the updated Order instance using OrderSerializer.

        params:
            instance (Order): Updated Order instance.
        return:
            dict: Serialized Order data.
        """
        return OrderSerializer(instance).data
