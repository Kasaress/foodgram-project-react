
from recipes.models import Follow
from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from users.models import CustomUser as User


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Follow.objects.filter(
                user=request.user.id,
                author=obj.id).exists() if request else False
