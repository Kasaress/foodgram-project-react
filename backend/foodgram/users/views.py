from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_401_UNAUTHORIZED

from recipes.models import Follow
from recipes.serializers import SubscribeSerializer, SubscriptionsSerializer
from users.serializers import CustomUserSerializer

User = get_user_model()

class UserViewSet(UserViewSet):
    """Вьюсет пользователей."""
    def get_queryset(self):
        return User.objects.all()


    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        """Подписка на автора и отписка от него."""
        user = request.user
        author = get_object_or_404(User, pk=id)
        data = {
            'user': user.id,
            'author': author.id,
        }
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscribe_to_del = Follow.objects.filter(
            user=request.user, author=author )
        if not subscribe_to_del:
            return Response(settings.SUBSCRIBE_ERROR_MESSAGE, status=status.HTTP_400_BAD_REQUEST)
        subscribe_to_del.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Список авторов, на которых подписан пользователь."""
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
    
    
    @action(methods=('GET',), detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
