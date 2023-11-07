from collections import defaultdict

from django_filters import rest_framework as filters
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter
from .models import (ShoppingCart, Ingredient, IngredientInRecipe,
                     Tag, Recipe, Favorite)
from .permissions import PublicAccess
from .serializers import (RecipeSerializer, RecipeListSerializer,
                          TagSerializer, IngredientSerializer,
                          FavoriteSerializer, ShoppingCartSerializer)


class RecipeListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = RecipeListPagination
    queryset = Recipe.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [PublicAccess]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [PublicAccess]


class FavoriteViewSet(viewsets.ModelViewSet):
    lookup_url_kwarg = 'recipe_id'
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get(self.lookup_url_kwarg)
        favorite = get_object_or_404(Recipe, id=int(recipe_id))
        user = self.request.user
        serializer.save(user=user, favorite=favorite)

    def destroy(self, request, recipe_id):
        favorite = get_object_or_404(Recipe, id=int(recipe_id))
        user = self.request.user
        try:
            favor = get_object_or_404(Favorite, user=user, favorite=favorite)
        except Favorite.DoesNotExist:
            return Response({'detail': 'The favorite object does not exist.'},
                            status=status.HTTP_404_NOT_FOUND)
        favor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    lookup_url_kwarg = 'recipe_id'
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer

    def perform_create(self, serializer):
        recipe_id = self.kwargs.get(self.lookup_url_kwarg)
        recipe = get_object_or_404(Recipe, id=int(recipe_id))
        user = self.request.user
        serializer.save(user=user, recipe=recipe)

    def destroy(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=int(recipe_id))
        user = self.request.user
        try:
            recipe_in_cart = get_object_or_404(ShoppingCart, user=user, recipe=recipe)
        except Favorite.DoesNotExist:
            return Response(
                {'detail': 'The ShoppingCart object does not exist.'},
                status=status.HTTP_404_NOT_FOUND)
        recipe_in_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartView(APIView):
    def get(self, request):
        user = self.request.user
        recipes_in_shopping_cart = user.shopping_cart.all()

        ingredients_summary = defaultdict(float)

        for cart_item in recipes_in_shopping_cart:
            recipe = cart_item.recipe
            ingredients_in_recipe = recipe.ingredientinrecipe_set.all()

            for ingredient_in_recipe in ingredients_in_recipe:
                ingredient = ingredient_in_recipe.ingredient
                amount = ingredient_in_recipe.amount
                measurement_unit = ingredient.measurement_unit

                ingredient_line = (f"{ingredient.name} ({amount} "
                                   f"{measurement_unit})")

                ingredients_summary[ingredient_line] += float(amount)

        content = "Список покупок:\n\n"

        for ingredient_line, amount in ingredients_summary.items():
            content += f"{ingredient_line} — {amount} г\n"

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_cart.txt"')

        return response
