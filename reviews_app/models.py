from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    """
    Represents a review given by a user (reviewer) to a business user.
    """
    business_user = models.ForeignKey(User, related_name='reviews_received', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, related_name='reviews_given', on_delete=models.CASCADE)
    rating = models.FloatField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
