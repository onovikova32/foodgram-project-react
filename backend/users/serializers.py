from djoser.serializers import UserCreateSerializer
from django.shortcuts import get_object_or_404
from django.urls import resolve
from rest_framework import serializers

from .models import CustomUser, Follow
from recipes.models import Recipe


class FollowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CustomUserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user.follow.filter(following=obj).exists()


class FollowListSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        recipes_limit = int(self.context['request'].query_params.get(
            'recipes_limit', 10))
        recipes = recipes[:recipes_limit]
        serialized_recipes = FollowRecipeSerializer(recipes, many=True).data

        return serialized_recipes

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user.follow.filter(following=obj).exists()


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'following')
        read_only_fields = ('user', 'following')

    def validate(self, data):
        user = self.context['request'].user
        match = resolve(self.context['request'].path_info)
        user_id = match.kwargs.get('user_id')
        following = get_object_or_404(CustomUser, id=user_id)
        if user == following:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')

        if user.follow.filter(following=following).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на данного автора')
        return data

    def to_representation(self, instance):
        return FollowListSerializer(instance.following,
                                    context=self.context).data
