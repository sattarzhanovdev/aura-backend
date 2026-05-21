import uuid

from django.db import models


class AiGenerationGroup(models.Model):
    REQUEST_TYPE_CHOICES = [
        ("outfit_generation", "Outfit Generation"),
    ]
    STATE_CHOICES = [
        ("queued", "Queued"),
        ("processing", "Processing"),
        ("success", "Success"),
        ("fail", "Fail"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_type = models.CharField(max_length=64, choices=REQUEST_TYPE_CHOICES)
    state = models.CharField(max_length=32, choices=STATE_CHOICES, default="queued")
    prompt = models.TextField()
    weather_summary = models.CharField(max_length=128, blank=True)
    occasion = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AiGenerationTask(models.Model):
    STATE_CHOICES = [
        ("waiting", "Waiting"),
        ("queuing", "Queuing"),
        ("generating", "Generating"),
        ("success", "Success"),
        ("fail", "Fail"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        AiGenerationGroup,
        related_name="tasks",
        on_delete=models.CASCADE,
    )
    variant_index = models.PositiveSmallIntegerField(default=0)
    provider_model = models.CharField(max_length=128, default="nano-banana-2")
    provider_task_id = models.CharField(max_length=255, unique=True)
    state = models.CharField(max_length=32, choices=STATE_CHOICES, default="waiting")
    prompt = models.TextField()
    input_image_urls = models.JSONField(default=list, blank=True)
    result_urls = models.JSONField(default=list, blank=True)
    callback_payload = models.JSONField(default=dict, blank=True)
    fail_code = models.CharField(max_length=64, blank=True)
    error_message = models.TextField(blank=True)
    progress = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
