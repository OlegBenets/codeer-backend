from django.db import models
from django.contrib.auth.models import User

class Offer(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, related_name='offers', on_delete=models.CASCADE)

    def __str__(self):
        return self.title