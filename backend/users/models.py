from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    username = models.CharField(
        verbose_name='username',
        max_length=settings.USER_STRING_FIELD_LENGTH,
        unique=True
    )
    email = models.EmailField(
        verbose_name='e-mail',
        max_length=settings.USER_EMAIL_FIELD_LENGTH,
        unique=True
    )
    first_name = models.TextField(
        verbose_name='first_name',
        max_length=settings.USER_STRING_FIELD_LENGTH
    )
    last_name = models.TextField(
        verbose_name='last_name',
        max_length=settings.USER_STRING_FIELD_LENGTH
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
