from rest_framework import serializers
from django.contrib.auth.models import User
from EcomApp.models import Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    name = serializers.CharField(source='display_name', read_only=True)
    class Meta:
        model = Profile
        fields = ['id', 'user', 'address', 'phone_number', 'role', 'name']
