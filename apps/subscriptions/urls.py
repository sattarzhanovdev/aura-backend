from django.urls import path

from .views import SubscriptionStatusView, SubscriptionVerifyView

urlpatterns = [
    path("verify", SubscriptionVerifyView.as_view()),
    path("status", SubscriptionStatusView.as_view()),
]
