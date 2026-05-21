from rest_framework import generics, response, views

from .selectors import list_user_wardrobe
from .serializers import ClothingItemSerializer
from .services import create_item_from_analysis


class WardrobeUploadView(views.APIView):
    def post(self, request, *args, **kwargs):
        image_url = request.data["image"]
        brand = request.data.get("brand", "")
        item = create_item_from_analysis(user=request.user, image_url=image_url, brand=brand)
        return response.Response(ClothingItemSerializer(item).data, status=201)


class WardrobeListView(generics.ListAPIView):
    serializer_class = ClothingItemSerializer

    def get_queryset(self):
        return list_user_wardrobe(self.request.user)


class WardrobeDeleteView(generics.DestroyAPIView):
    serializer_class = ClothingItemSerializer

    def get_queryset(self):
        return list_user_wardrobe(self.request.user)
