from django.urls import path
from .views import (
    RegistrationView, LoginView,
    ProfileDetailView, BusinessUserListView, CustomerUserListView
)

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),

    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/business/', BusinessUserListView.as_view(), name='business-profile-list'),
    path('profiles/customer/', CustomerUserListView.as_view(), name='customer-profile-list'),
]