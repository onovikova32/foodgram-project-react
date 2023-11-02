from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import IngredientSerializer, TagSerializer
from recipes.models import Ingredient, Tag


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = IngredientSerializer


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = TagSerializer
