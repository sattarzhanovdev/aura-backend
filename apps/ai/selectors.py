from collections import Counter

from apps.outfits.models import OutfitGeneration
from apps.wardrobe.models import ClothingItem


def build_style_profile(user):
    items = list(ClothingItem.objects.filter(user=user))
    colors = Counter(item.color for item in items)
    tags = Counter(tag for item in items for tag in item.style_tags)
    usage = OutfitGeneration.objects.filter(user=user).count()
    return {
        "style_label": "Minimal Streetwear",
        "palette": [color for color, _ in colors.most_common(3)],
        "top_aesthetics": [tag for tag, _ in tags.most_common(3)],
        "relaxed_silhouettes": True,
        "generation_count": usage,
    }
