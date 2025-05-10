from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from apps.accounts.models import Profile
from .serializers import ProfileSerializer
from .serializers import RegistrationSerializer, LoginSerializer

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id,
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.method == 'PATCH' and obj.user != self.request.user:
            raise PermissionDenied("You can only update your own profile.")
        return obj


class BusinessProfileListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(type='business')


class CustomerProfileListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(type='customer')