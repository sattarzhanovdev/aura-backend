from django.urls import path

from .views import (
    ClothingAnalysisView,
    KieCallbackView,
    OutfitGenerationCreateView,
    OutfitGenerationDetailView,
    StyleProfileView,
)

urlpatterns = [
    path("profile", StyleProfileView.as_view()),
    path("clothing/analyze", ClothingAnalysisView.as_view()),
    path("outfit-groups", OutfitGenerationCreateView.as_view()),
    path("outfit-groups/<uuid:group_id>", OutfitGenerationDetailView.as_view()),
    path("kie/callback", KieCallbackView.as_view()),
]
