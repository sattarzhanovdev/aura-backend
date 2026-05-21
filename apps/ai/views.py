from rest_framework import permissions, response, status, views

from .selectors import build_style_profile
from .services import (
    KieConfigurationError,
    analyze_clothing_from_image,
    create_outfit_generation_group,
    handle_kie_callback,
    refresh_generation_group,
    serialize_group,
)


class StyleProfileView(views.APIView):
    def get(self, request, *args, **kwargs):
        return response.Response(build_style_profile(request.user))


class ClothingAnalysisView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            result = analyze_clothing_from_image(base64_data=request.data["image_base64"])
        except KeyError:
            return response.Response(
                {"detail": "image_base64 is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except KieConfigurationError as exc:
            return response.Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response.Response(result)


class OutfitGenerationCreateView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            group = create_outfit_generation_group(
                wardrobe_items=request.data.get("wardrobe_items", []),
                image_base64_list=request.data.get("image_base64_list", []),
                weather=request.data.get("weather", "Weather unavailable"),
                occasion=request.data.get("occasion", "Daily"),
                variant_count=min(max(int(request.data.get("variant_count", 3)), 1), 3),
            )
        except KieConfigurationError as exc:
            return response.Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return response.Response(serialize_group(group), status=status.HTTP_201_CREATED)


class OutfitGenerationDetailView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, group_id, *args, **kwargs):
        group = refresh_generation_group(group_id)
        return response.Response(serialize_group(group))


class KieCallbackView(views.APIView):
    permission_classes = [permissions.AllowAny]

    authentication_classes = []

    def get(self, request, *args, **kwargs):
        return response.Response({"status": "ready", "detail": "KIE callback endpoint is reachable."})

    def post(self, request, *args, **kwargs):
        handle_kie_callback(request.data)
        return response.Response({"status": "ok"})
