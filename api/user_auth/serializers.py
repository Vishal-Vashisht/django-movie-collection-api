from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("username", "password")
        extra_kwargs = {
            "username": {"write_only": True},
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        """
        Create the user object in the database
        """
        user = user = User.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        refresh = RefreshToken.for_user(instance)
        representation["access"] = str(refresh.access_token)
        return representation
