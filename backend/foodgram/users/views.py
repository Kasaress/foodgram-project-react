from rest_framework.views import APIView
# from users.serializers import  SignUpSerializer
from django.contrib.auth import get_user_model
# from django.db import IntegrityError
# from django.conf import settings
# from rest_framework.response import Response
# from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from djoser.views import UserViewSet

User = get_user_model()

class UserViewSet(UserViewSet):
    def get_queryset(self):
        return User.objects.all()
