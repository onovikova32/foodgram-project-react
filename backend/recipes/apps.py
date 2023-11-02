from django.apps import AppConfig


class RecipesConfig(AppConfig):
    name = 'recipes'
    verbose_name = 'Рецепты'


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = 'Пользователи'


class ApiConfig(AppConfig):
    name = 'api'
    verbose_name = 'API'
