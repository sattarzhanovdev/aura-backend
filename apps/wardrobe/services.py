from dataclasses import dataclass

from .models import ClothingItem


@dataclass
class ClothingAnalysis:
    category: str
    subcategory: str
    color: str
    season: str
    style_tags: list[str]
    formality_level: str


def analyze_clothing(image_url: str) -> ClothingAnalysis:
    # Placeholder for OpenAI / Gemini / HF integration.
    return ClothingAnalysis(
        category="tops",
        subcategory="t-shirts",
        color="white",
        season="all-season",
        style_tags=["minimal", "streetwear"],
        formality_level="casual",
    )


def create_item_from_analysis(*, user, image_url: str, brand: str = "") -> ClothingItem:
    analysis = analyze_clothing(image_url)
    return ClothingItem.objects.create(
        user=user,
        image=image_url,
        category=analysis.category,
        subcategory=analysis.subcategory,
        color=analysis.color,
        season=analysis.season,
        style_tags=analysis.style_tags,
        brand=brand,
        formality_level=analysis.formality_level,
    )
