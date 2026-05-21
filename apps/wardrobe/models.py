from django.conf import settings
from django.db import models


class ClothingItem(models.Model):
    CATEGORY_CHOICES = [
        ("tops", "Tops"),
        ("bottoms", "Bottoms"),
        ("shoes", "Shoes"),
        ("accessories", "Accessories"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.URLField()
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=64)
    color = models.CharField(max_length=64)
    season = models.CharField(max_length=32)
    style_tags = models.JSONField(default=list, blank=True)
    brand = models.CharField(max_length=128, blank=True)
    formality_level = models.CharField(max_length=32, default="casual")
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
