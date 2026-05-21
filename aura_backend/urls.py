from django.urls import include, path

urlpatterns = [
    path("api/auth/", include("apps.auth_app.urls")),
    path("api/wardrobe/", include("apps.wardrobe.urls")),
    path("api/outfits/", include("apps.outfits.urls")),
    path("api/style/", include("apps.ai.urls")),
    path("api/subscription/", include("apps.subscriptions.urls")),
]
