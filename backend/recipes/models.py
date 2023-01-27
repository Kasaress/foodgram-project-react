from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from recipes import validators
from users.models import CustomUser as User


class Tag(models.Model):
    """Модель тэга."""
    name = models.CharField(
        max_length=settings.NAME_SLUG_LENGTH,
        verbose_name='Тэг'
    )
    color = models.CharField(
        max_length=settings.COLOR_FIELD_LENGTH,
        default="#E26C2D",
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=settings.NAME_SLUG_LENGTH,
        unique=True,
        validators=[validators.validate_slug],
        verbose_name='slug'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
        max_length=settings.NAME_SLUG_LENGTH,
        verbose_name='Ингредиент'
    )
    measurement_unit = models.CharField(
        max_length=settings.NAME_SLUG_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            ),
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=settings.NAME_SLUG_LENGTH,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Картинка'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(
            1, message='Время приготовления не может быть меньше 1 минуты.'
        )]
    )
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

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    """Модель для связи рецептов и тэгов."""
    tag = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    recipe = models.ForeignKey(
        Recipe,
        models.SET_NULL,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Связь тэга с рецептом'
        verbose_name_plural = 'Связи тэгов с рецептами'

    def __str__(self):
        return f'Тэг "{self.tag}" в рецепте {self.recipe}'


class IngredientRecipe(models.Model):
    """Модель для связи рецептов и ингредиентов."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='ingrs_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='ingrs_recipes'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1, message='Количество не может быть нулевым.'
        )]
    )

    class Meta:
        verbose_name = 'Связь ингредиента с рецептом'
        verbose_name_plural = 'Связи ингредиентов с рецептами'

    def __str__(self):
        return f'Ингредиент "{self.ingredient}" в рецепте {self.recipe}'


class FavoriteShoppingCartBaseModel(models.Model):
    """Родительская модель для избранного и списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        )
    recipe = models.ForeignKey(
        Recipe,
        models.CASCADE,
        )

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(class)s_unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'Пользователь {self.user}, рецепт {self.recipe}'


class Favorite(FavoriteShoppingCartBaseModel):
    """Модель избранного."""
    class Meta(FavoriteShoppingCartBaseModel.Meta):
        verbose_name = 'Избранное'
        default_related_name = 'favorite'


class ShoppingCart(FavoriteShoppingCartBaseModel):
    """Модель списка покупок."""
    class Meta(FavoriteShoppingCartBaseModel.Meta):
        verbose_name = 'Список покупок'
        default_related_name = 'shopping_cart'


class Follow(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
        ]
        verbose_name_plural = 'Подписки'
        verbose_name = 'Подписка'
