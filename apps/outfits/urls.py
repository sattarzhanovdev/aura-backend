from django.urls import path

from .views import OutfitGenerateView, OutfitHistoryView

urlpatterns = [
    path("generate", OutfitGenerateView.as_view()),
    path("history", OutfitHistoryView.as_view()),
]
