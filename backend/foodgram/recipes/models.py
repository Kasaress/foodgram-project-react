from django.db import models
from django.conf import settings
from . import validators
from django.contrib.auth import get_user_model

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
    image = models.TextField()
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