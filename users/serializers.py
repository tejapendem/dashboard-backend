# users/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomUser, Team
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()




class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']
        
# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ('id', 'username', 'email', 'password')

#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         return user


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'username', 'email')

# class TeamSerializer(serializers.ModelSerializer):
#     members = UserSerializer(many=True, read_only=True)

#     class Meta:
#         model = Team
#         fields = ('id', 'name', 'members')



# class TeamSerializer(serializers.ModelSerializer):
#     members = UserSerializer(many=True)

#     class Meta:
#         model = Team
#         fields = ['id', 'name', 'members', 'created_at']