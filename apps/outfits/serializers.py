from rest_framework import serializers

from .models import OutfitGeneration


class OutfitGenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutfitGeneration
        fields = "__all__"
        read_only_fields = ["user", "created_at"]
