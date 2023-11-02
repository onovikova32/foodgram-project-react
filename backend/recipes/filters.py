import django_filters
from .models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.NumberFilter(method='get_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(method='get_is_in_shopping_cart')
    tags = django_filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                                    queryset=Tag.objects.all(),
                                                    to_field_name='slug')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
