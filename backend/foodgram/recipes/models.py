from django.db import models
from django.conf import settings
from . import validators
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint

User = get_user_model()

class Tag(models.Model):
    name = models.CharField(max_length=settings.NAME_SLUG_LENGTH )
    color = models.CharField(max_length=7, default="#E26C2D")
    slug = models.SlugField(
        max_length=settings.NAME_SLUG_LENGTH,
        unique=True,
        validators=[validators.validate_slug,]
    )
    
    def __str__(self):
        return self.name
    
    
class Ingredient(models.Model):
    name = models.CharField(max_length=settings.NAME_SLUG_LENGTH)
    measurement_unit = models.CharField(max_length=settings.NAME_SLUG_LENGTH)
    
    def __str__(self):
        return self.name
    
    
class Recipe(models.Model):    
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True, 
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(max_length=settings.NAME_SLUG_LENGTH )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка'
    )
    text = models.TextField()
    cooking_time = models.IntegerField()
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Тэги',
        help_text='Выберите тэги',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты',
        related_name='recipes',
    )
    
    def __str__(self):
        return self.name
      
    
class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    recipe = models.ForeignKey(
        Recipe, 
        models.SET_NULL,
        blank=True,
        null=True)

    def __str__(self):
        return f'{self.tag}{self.recipe}'
    
    
    
class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    recipe = models.ForeignKey(
        Recipe, 
        models.SET_NULL,
        blank=True,
        null=True)
    amount = models.IntegerField()

    def __str__(self):
        return f'{self.ingredient}{self.recipe}'
    
    
    
class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite'
        )
    recipe = models.ForeignKey(
        Recipe, 
        models.CASCADE,
        related_name='favorite'
        )

    def __str__(self):
        return f'У пользователя {self.user} в избранном {self.recipe}'
    
    
class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_card'
        )
    recipe = models.ForeignKey(
        Recipe, 
        models.CASCADE,
        related_name='shopping_card'
        )

    def __str__(self):
        return f'У пользователя {self.user} в списке покупок {self.recipe}'
    
    
class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
        ]
        verbose_name_plural = 'Подписки'
        verbose_name = 'Подписка'