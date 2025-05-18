from django.urls import path, include
from rest_framework import routers
from .views import OfferViewset, OfferDetailsViewSet

router = routers.SimpleRouter()
router.register(r'offers', OfferViewset, basename='offers')
router.register(r'offerdetails', OfferDetailsViewSet, basename='offerdetails')

urlpatterns = [
    path('', include(router.urls)),
]