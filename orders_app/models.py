from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):
    """
    Represents an order placed by a customer user for a specific offer detail.
    """

    customer_user = models.ForeignKey(User, related_name="orders_as_customer", on_delete=models.CASCADE)
    business_user = models.ForeignKey(User, related_name="orders_as_business", on_delete=models.CASCADE)
    offer_detail = models.ForeignKey("offers_app.OfferDetails", on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="in_progress")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
