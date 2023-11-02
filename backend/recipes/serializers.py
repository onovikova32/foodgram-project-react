import base64
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers
from users.serializers import CustomUserSerializer

from .models import Recipe, IngredientInRecipe, Ingredient,\
    Tag, Favorite, ShoppingCart


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if data.startswith('data:image'):
            img_format, img_str = data.split(';base64,')
            ext = img_format.split('/')[-1]

            data = ContentFile(base64.b64decode(img_str),
                               name=f'uploaded_image.{ext}')

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1, max_value=9999)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = AddIngredientSerializer(many=True,
                                          source='ingredientinrecipe_set')
    image = Base64ImageField(write_only=True, required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'name', 'text', 'image',
                  'cooking_time')

    def validate(self, data):
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError({'tags': 'Нужно выбрать '
                                                       'хотя бы один тег!'})
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({'tags': 'Теги не уникальны!'})
        return data

    def create(self, validated_data):
        with transaction.atomic():
            tags_data = validated_data.pop('tags')
            ingredients_data = validated_data.pop('ingredientinrecipe_set')

            recipe = Recipe.objects.create(**validated_data)

            for tag in tags_data:
                recipe.tags.add(tag)

            for ingredient_data in ingredients_data:
                primary_key = ingredient_data['id']
                amount = ingredient_data['amount']
                IngredientInRecipe.objects.create(recipe=recipe,
                                                  ingredient=primary_key,
                                                  amount=amount)

            return recipe

    def update(self, instance, validated_data):
        with transaction.atomic():
            tags_data = validated_data.pop('tags')
            ingredients_data = validated_data.pop('ingredientinrecipe_set')

            # Обновление общих полей рецепта
            instance.name = validated_data.get('name', instance.name)
            instance.text = validated_data.get('text', instance.text)
            instance.text = validated_data.get('image', instance.image)
            instance.cooking_time = validated_data.get('cooking_time',
                                                       instance.cooking_time)
            instance.save()

            # Обновление тегов
            instance.tags.set(tags_data)

            # Удаление старых ингредиентов и добавление новых
            instance.ingredientinrecipe_set.all().delete()
            for ingredient_data in ingredients_data:
                IngredientInRecipe.objects.create(recipe=instance,
                                                  **ingredient_data)

            return instance


class RecipeListSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(many=True,
                                               source='ingredientinrecipe_set')
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(many=False, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        is_favorited = obj.favorite.filter(user=user).exists()

        return is_favorited

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        is_in_shopping_cart = obj.shopping_cart.filter(user=user).exists()

        return is_in_shopping_cart


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'favorite')
        read_only_fields = ('user', 'favorite')

    # def validate(self, data):
    #     follow = self.context['request'].user
    #     match = resolve(self.context['request'].path_info)
    #     user_id = match.kwargs.get('user_id')
    #     print(user_id)
    #     following = get_object_or_404(CustomUser, id=user_id)
    #     if follow == following:
    #         raise serializers.ValidationError(
    #             'Нельзя подписаться на самого себя')
    #
    #     if Follow.objects.filter(
    #             user=follow, following=following).exists():
    #         raise serializers.ValidationError(
    #             'Вы уже подписаны на данного автора')
    #     return data

    def to_representation(self, instance):
        return FavoriteRecipeSerializer(instance.favorite,
                                        context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')

    # def validate(self, data):
    #     follow = self.context['request'].user
    #     match = resolve(self.context['request'].path_info)
    #     user_id = match.kwargs.get('user_id')
    #     print(user_id)
    #     following = get_object_or_404(CustomUser, id=user_id)
    #     if follow == following:
    #         raise serializers.ValidationError(
    #             'Нельзя подписаться на самого себя')
    #
    #     if Follow.objects.filter(
    #             user=follow, following=following).exists():
    #         raise serializers.ValidationError(
    #             'Вы уже подписаны на данного автора')
    #     return data

    def to_representation(self, instance):
        return FavoriteRecipeSerializer(instance.recipe,
                                        context=self.context).data
