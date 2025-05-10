from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.reviews.models import Review
from apps.accounts.models import Profile
from apps.offers.models import Offer
from django.db.models import Avg

class BaseInfoAPIView(APIView):
    def get(self, request):
        review_count = Review.objects.count()
        avg = Review.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0.0
        average_rating = round(avg, 1)
        business_profile_count = Profile.objects.filter(type='business').count()
        offer_count = Offer.objects.count()

        data = {
            'review_count': review_count,
            'average_rating': average_rating,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count
        }
        return Response(data, status=status.HTTP_200_OK)