from django.urls import path

from .views import WardrobeDeleteView, WardrobeListView, WardrobeUploadView

urlpatterns = [
    path("upload", WardrobeUploadView.as_view()),
    path("items", WardrobeListView.as_view()),
    path("item/<int:pk>", WardrobeDeleteView.as_view()),
]
