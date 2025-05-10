from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed
from apps.accounts.models import Profile

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=[('customer', 'Customer'), ('business', 'Business')], write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')
        user = User.objects.create_user(**validated_data)
        user.profile.type = user_type  # Falls du ein Profile-Modell mit "type"-Feld hast
        user.profile.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        user = authenticate(username=data['username'], password=data['password'])

        if not user:
            raise AuthenticationFailed("Invalid credentials.")
        return {'user': user}


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'bio', 'location', 'avatar']