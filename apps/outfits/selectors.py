from .models import OutfitGeneration


def list_generation_history(user):
    return OutfitGeneration.objects.filter(user=user).order_by("-created_at")
