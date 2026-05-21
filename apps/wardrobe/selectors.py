from .models import ClothingItem


def list_user_wardrobe(user):
    return ClothingItem.objects.filter(user=user).order_by("-created_at")
