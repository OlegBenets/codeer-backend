from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.authtoken.models import Token
from auth_app.models import Profile
from .serializers import ProfileSerializer, RegistrationSerializer, LoginSerializer, BusinessUserListSerializer, CustomerUserListSerializer
from django.shortcuts import get_object_or_404


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieve the Profile where the associated user's ID matches the URL parameter.
        """
        user_id = self.kwargs["pk"]
        obj = get_object_or_404(Profile, user__id=user_id)

        if self.request.method in ['PATCH', 'PUT']:
            if not self.request.user.is_staff and obj.user != self.request.user:
                raise PermissionDenied("You can only edit your own profile.")

        return obj


class BusinessUserListView(generics.ListAPIView):
    serializer_class = BusinessUserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(type='business')


class CustomerUserListView(generics.ListAPIView):
    serializer_class = CustomerUserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(type='customer')


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    