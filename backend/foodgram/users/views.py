from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from recipes.models import Follow
from rest_framework.response import Response
from rest_framework import status
from users.serializers import CustomUserSerializer
from recipes.serializers import SubscribeSerializer, SubscriptionsSerializer
from rest_framework.status import HTTP_401_UNAUTHORIZED


User = get_user_model()

class UserViewSet(UserViewSet):

    def get_queryset(self):
        return User.objects.all()


    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)
        data = {
            'user': user.id,
            'author': author.id,
        }
        print(data)
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
            return Response({'errors': 'Вы не были подписаны на этого пользователя.'}, status=status.HTTP_400_BAD_REQUEST)
        subscribe_to_del.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
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
