from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from djoser.views import UserViewSet
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from django.shortcuts import get_object_or_404
from recipes.models import Follow
from rest_framework.response import Response
from rest_framework import status, viewsets
from users.serializers import SubscribeSerializer, SubscriptionsSerializer
from rest_framework.pagination import PageNumberPagination


User = get_user_model()

class UserViewSet(UserViewSet):
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
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
        get_object_or_404(
            Follow, user=user, author=author
        ).delete()
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
