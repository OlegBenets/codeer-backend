from django.db import models
from django.contrib.auth.models import User  # Angenommen, wir nutzen Django's User Modell

class OfferDetail(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    business_user = models.ForeignKey(User, related_name='offer_details', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer_user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    business_user = models.ForeignKey(User, related_name='business_orders', on_delete=models.CASCADE)
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()  # Für Features als Liste
    offer_type = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.title}"
