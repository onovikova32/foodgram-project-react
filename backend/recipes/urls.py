from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import TagViewSet, IngredientViewSet, RecipeViewSet, FavoriteViewSet,\
    ShoppingCartViewSet, DownloadShoppingCartView

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [path('recipes/download_shopping_cart/',
                    DownloadShoppingCartView.as_view(),
                    name='download_shopping_cart'),
               path('', include(router.urls)),
               path('recipes/<int:recipe_id>/favorite/', FavoriteViewSet.as_view({'post': 'create',
                                                                                  'delete': 'destroy'}),
                    name='favorite'),
               path('recipes/<int:recipe_id>/shopping_cart/',
                    ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
                    name='shopping_cart'),
               ]
