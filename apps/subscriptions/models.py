from django.conf import settings
from django.db import models


class Subscription(models.Model):
    PLAN_CHOICES = [("free", "Free"), ("premium", "Premium")]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False)
    subscription_type = models.CharField(max_length=32, choices=PLAN_CHOICES, default="free")
    subscription_expires = models.DateTimeField(null=True, blank=True)
    daily_generation_limit = models.PositiveIntegerField(default=3)
    provider = models.CharField(max_length=32, blank=True)
