from rest_framework import generics, response, views

from .selectors import list_generation_history
from .serializers import OutfitGenerationSerializer
from .services import generate_outfit


class OutfitGenerateView(views.APIView):
    def post(self, request, *args, **kwargs):
        generation = generate_outfit(
            user=request.user,
            weather=request.data.get("weather", "22C sunny"),
            occasion=request.data.get("occasion", "daily"),
            aesthetic=request.data.get("aesthetic", "minimal streetwear"),
        )
        return response.Response(OutfitGenerationSerializer(generation).data, status=201)


class OutfitHistoryView(generics.ListAPIView):
    serializer_class = OutfitGenerationSerializer

    def get_queryset(self):
        return list_generation_history(self.request.user)
