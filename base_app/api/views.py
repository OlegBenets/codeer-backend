from rest_framework import status
from rest_framework.response import Response
from offers_app.models import Offer
from reviews_app.models import Review
from auth_app.models import Profile
from rest_framework.views import APIView
from django.db.models import Avg


class BaseInfoViewset(APIView):
    """
    API endpoint to retrieve general statistics about the platform.
    """

    def get(self, request):
        """
        Return statistics including:
        - Total review count
        - Average rating
        - Business profile count
        - Offer count

        return:
            Response: JSON with stats data.
        """
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(avg_rating=Avg("rating"))["avg_rating"]
        average_rating = round(average_rating, 1) if average_rating is not None else 0.0
        business_profile_count = Profile.objects.filter(type="business").count()
        offer_count = Offer.objects.count()

        return Response(
            {
                "review_count": review_count,
                "average_rating": average_rating,
                "business_profile_count": business_profile_count,
                "offer_count": offer_count,
            },
            status=status.HTTP_200_OK,
        )
