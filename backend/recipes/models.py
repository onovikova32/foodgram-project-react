from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    measurement_unit = models.CharField(max_length=10,
                                        verbose_name='Единица измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255,
                            unique=True,
                            verbose_name='Название')
    color = models.CharField(max_length=7, verbose_name='Цвет')
    slug = models.SlugField(unique=True, verbose_name='Слаг')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    MAX_COOKING_TIME = 32000
    MIN_COOKING_TIME = 1

    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(max_length=255, verbose_name='Название')
    image = models.ImageField(upload_to='recipe_images/',
                              blank=True,
                              null=True,
                              verbose_name='Картинка')
    text = models.TextField(verbose_name='Текст')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(MIN_COOKING_TIME,
                              message=f'Минимальное время - '
                                      f'{MIN_COOKING_TIME}'),
            MaxValueValidator(MAX_COOKING_TIME,
                              message=f'Максимальное время - '
                                      f'{MAX_COOKING_TIME}')
        ]
    )
    ingredients = models.ManyToManyField(Ingredient,
                                         through='IngredientInRecipe',
                                         blank=False,
                                         verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag, verbose_name='Теги')

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    MAX_AMOUNT = 32000
    MIN_AMOUNT = 1

    ingredient = models.ForeignKey(Ingredient,
                                   on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(MIN_AMOUNT,
                              message=f'Минимальное время - {MIN_AMOUNT}'),
            MaxValueValidator(MAX_AMOUNT,
                              message=f'Максимальное время - {MAX_AMOUNT}')
        ]
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингредиентов в рецепте'
        verbose_name_plural = 'Ингредиентов в рецепте'

    def __str__(self):
        return f"{self.ingredient.name} ({self.amount} " \
               f"{self.ingredient.measurement_unit}) in {self.recipe.name}"


class Favorite(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorite',
                             verbose_name='Пользователь'
                             )
    favorite = models.ForeignKey(Recipe,
                                 on_delete=models.CASCADE,
                                 related_name='favorite',
                                 verbose_name='Избранное')

    class Meta:
        ordering = ('user',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='shopping_cart',
                             verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='shopping_cart',
                               verbose_name='Рецепт')

    class Meta:
        ordering = ('user',)
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
