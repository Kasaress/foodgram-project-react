
from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Follow, Recipe
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework import serializers, status
from rest_framework.serializers import SerializerMethodField


User = get_user_model()
        
class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password')
        
    def create(self, validated_data): # переопределение для хранения хэша пароля
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

        return Follow.objects.filter(
            user=user.id,
            author=obj.id).exists()
        
        
class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
        
class SubscribeSerializer(CustomUserSerializer):
    queryset = User.objects.all()
    # author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ('user', 'author')


    def validate(self, data):
        print(data)
        user = data['user']
        author = data['author']
        if Follow.objects.filter(
            user=user,
            author=author
        ).exists():
            raise ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

