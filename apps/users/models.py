from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    profile_photo = models.URLField(blank=True)
    gender = models.CharField(max_length=32, blank=True)
    style_preferences = models.JSONField(default=list, blank=True)
    favorite_colors = models.JSONField(default=list, blank=True)
    lifestyle_tags = models.JSONField(default=list, blank=True)
    body_type = models.CharField(max_length=64, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    subscription_status = models.CharField(max_length=32, default="free")
    subscription_expire_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
