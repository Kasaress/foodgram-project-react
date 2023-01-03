
from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Follow, Recipe
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework import serializers, status
from rest_framework.serializers import SerializerMethodField
# from recipes.serializers import ShortRecipeSerializer


User = get_user_model()
        
class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password')
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(
            **validated_data
        )
        user.set_password(password)
        user.save()
        return user
    
    
class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = SerializerMethodField()
    class Meta:
        model = User
        fields = ('email', 
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed'
                  )
        
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request:
            user = request.user
            if user.is_anonymous:
                return False
            return Follow.objects.filter(
                user=user.id,
                author=obj.id).exists()
        return False
        
        
