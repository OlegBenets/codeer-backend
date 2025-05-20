from django.db import models
from django.contrib.auth.models import User


class Offer(models.Model):
    """
    Represents an offer created by a business user.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Untitled Offer")
    image = models.FileField(upload_to="uploads/", null=True, blank=True)
    description = models.TextField(max_length=255, default="No description provided")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]


class OfferDetails(models.Model):
    """
    Represents detailed information of an offer, such as price, delivery time, and features.
    """

    offer = models.ForeignKey(Offer, related_name="offer_details", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Untitled Detail")
    revisions = models.IntegerField(default=0)
    delivery_time_in_days = models.IntegerField(null=True, blank=True, default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=50, null=True, blank=True, default="basic")
