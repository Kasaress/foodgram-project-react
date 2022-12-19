from django.shortcuts import render
from rest_framework.views import APIView
from users.serializers import  SignUpSerializer
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.conf import settings
from rest_framework.response import Response
from rest_framework import filters, mixins, permissions, status, viewsets

User = get_user_model()

class RegisterView(APIView):
    """Регистирирует пользователя."""
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        username = serializer.validated_data.get('username')
        first_name = serializer.validated_data.get('first_name')
        last_name = serializer.validated_data.get('last_name')
        password = serializer.validated_data.get('password')
        
        try:
            user = User.objects.get_or_create(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password,
                )
        except IntegrityError:
            message = (
                settings.DUPLICATE_USERNAME_MESSAGE
            )
            return Response(
                message,
                status=status.HTTP_400_BAD_REQUEST)
        # user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)