from django.urls import path, include
from rest_framework import routers
from .views import ReviewViewSet

router = routers.SimpleRouter()
router.register(r'', ReviewViewSet, basename='reviews')

urlpatterns = [
    path('', include(router.urls)),
]