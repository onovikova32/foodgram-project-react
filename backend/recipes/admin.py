from django.contrib import admin
from .models import Recipe, Ingredient, Tag, Favorite


class IngredientInRecipeInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInRecipeInline,)
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'

    def total_favorites(self, obj):
        return obj.favorite.count()

    total_favorites.short_description = 'Избранное'
    list_display += ('total_favorites',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'favorite')
    list_filter = ('user',)
    empty_value_display = '-пусто-'
