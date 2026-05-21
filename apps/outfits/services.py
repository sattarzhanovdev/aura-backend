from apps.wardrobe.models import ClothingItem

from .models import OutfitGeneration


def build_outfit_prompt(*, wardrobe, weather: str, occasion: str, aesthetic: str) -> str:
    top_pieces = ", ".join(item.subcategory for item in wardrobe[:3])
    return (
        f"{aesthetic} outfit, occasion {occasion}, weather {weather}, wardrobe options: {top_pieces}, "
        "cinematic fashion photography, soft shadows, premium editorial style"
    )


def generate_outfit(*, user, weather: str, occasion: str, aesthetic: str) -> OutfitGeneration:
    wardrobe = list(ClothingItem.objects.filter(user=user)[:12])
    prompt = build_outfit_prompt(
        wardrobe=wardrobe,
        weather=weather,
        occasion=occasion,
        aesthetic=aesthetic,
    )
    result = {
        "top": "white oversized hoodie",
        "bottom": "black cargos",
        "shoes": "white sneakers",
        "accessories": ["silver watch"],
        "style_reasoning": "clean minimal streetwear outfit",
    }
    return OutfitGeneration.objects.create(
        user=user,
        prompt=prompt,
        occasion=occasion,
        weather_summary=weather,
        result=result,
        preview_image="",
    )
