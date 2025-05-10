from django.db import models
from django.contrib.auth.models import User
from apps.offers.models import Offer

class Review(models.Model):
    offer = models.ForeignKey(Offer, related_name='reviews', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.reviewer.username} for {self.offer.title}'
