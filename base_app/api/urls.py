from django.urls import path
from .views import BaseInfoViewset

urlpatterns = [
    path('', BaseInfoViewset.as_view(), name='base-info')
]