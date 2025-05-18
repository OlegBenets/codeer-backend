from rest_framework import serializers
from auth_app.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator


def get_file_url(obj, context):
    request = context.get('request')
    if obj.file and request:
        return request.build_absolute_uri(obj.file.url)
    return None


class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pk', 'username', 'first_name', 'last_name']


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name", required=False, allow_blank=True)
    last_name = serializers.CharField(source="user.last_name", required=False, allow_blank=True)
    file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = '__all__'

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        file = validated_data.pop("file", None)

        user = instance.user
        for attr in ['first_name', 'last_name']:
            if attr in user_data:
                setattr(user, attr, user_data[attr])
        user.save()

        if file:
            instance.file = file

        return super().update(instance, validated_data)



class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150, 
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, min_length=6)
    repeated_password = serializers.CharField(write_only=True, min_length=6)
    type = serializers.ChoiceField(choices=Profile.USER_TYPES, default='customer')

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({"repeated_password": "Die Passwörter stimmen nicht überein."})
        
        password = data['password']
        if len(password) < 8:
            raise serializers.ValidationError({"password": "Das Passwort muss mindestens 8 Zeichen lang sein."})
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError({"password": "Das Passwort muss mindestens eine Zahl enthalten."})
        if not any(char.islower() for char in password):
            raise serializers.ValidationError({"password": "Das Passwort muss mindestens einen Kleinbuchstaben enthalten."})
        if not any(char.isupper() for char in password):
            raise serializers.ValidationError({"password": "Das Passwort muss mindestens einen Großbuchstaben enthalten."})

        return data

    def create(self, validated_data):
        repeated_password = validated_data.pop('repeated_password')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        profile_type = validated_data.get('type', 'customer') 
        Profile.objects.create(user=user, email=validated_data.get('email', ''), type=profile_type, name=user.username)
        
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data.get("username"), password=data.get("password"))
        if not user:
            raise serializers.ValidationError({"detail": ["Ungültige Anmeldeinformationen."]})

        token, _ = Token.objects.get_or_create(user=user)

        return {
            "token": token.key,
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }


class BusinessUserListSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)
    file = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user', 'file', 'location', 'tel', 'description', 'working_hours', 'type']

    def get_file(self, obj):
        return get_file_url(obj, self.context)


class CustomerUserListSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)
    file = serializers.SerializerMethodField()
    uploaded_at = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['user', 'file', 'location', 'tel', 'description', 'uploaded_at', 'type']

    def get_file(self, obj):
        return get_file_url(obj, self.context)

    def get_uploaded_at(self, obj):
        return obj.created_at
