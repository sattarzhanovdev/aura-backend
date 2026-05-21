from rest_framework import response, views

from .models import Subscription


class SubscriptionVerifyView(views.APIView):
    def post(self, request, *args, **kwargs):
        subscription, _ = Subscription.objects.get_or_create(user=request.user)
        subscription.provider = request.data.get("provider", "manual")
        subscription.save(update_fields=["provider"])
        return response.Response({"status": "received", "provider": subscription.provider})


class SubscriptionStatusView(views.APIView):
    def get(self, request, *args, **kwargs):
        subscription, _ = Subscription.objects.get_or_create(user=request.user)
        return response.Response(
            {
                "is_premium": subscription.is_premium,
                "subscription_type": subscription.subscription_type,
                "subscription_expires": subscription.subscription_expires,
                "daily_generation_limit": subscription.daily_generation_limit,
            }
        )
