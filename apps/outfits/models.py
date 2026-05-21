from django.conf import settings
from django.db import models


class OutfitGeneration(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prompt = models.TextField()
    occasion = models.CharField(max_length=64, blank=True)
    weather_summary = models.CharField(max_length=128, blank=True)
    result = models.JSONField(default=dict)
    preview_image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
