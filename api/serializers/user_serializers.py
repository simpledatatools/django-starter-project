from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils import timezone

from accounts.models import *
from backend.models import *


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "name", "profile_photo"]

    def get_name(self, obj):
        return obj.first_name or obj.email

    def get_profile_photo(self, obj):
        profile_photo = getattr(obj, "profile_photo", None)
        return profile_photo.file.url if profile_photo else None


class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["token"]

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["id"] = instance.id
        data["profile_photo"] = self.get_profile_photo(instance)
        return data

    def get_profile_photo(self, obj):
        profile_photo = getattr(obj, "profile_photo", None)
        return profile_photo.file.url if profile_photo else None
