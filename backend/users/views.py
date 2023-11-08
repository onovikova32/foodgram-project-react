from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import generics, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Follow, CustomUser
from .serializers import FollowListSerializer, FollowSerializer


class FollowListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        recipes_limit = self.request.query_params.get('recipes_limit', None)
        if recipes_limit is not None:
            recipes_limit = int(recipes_limit)

        return super().get_paginated_response(data)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)


class FollowListViewSet(generics.ListAPIView):
    serializer_class = FollowListSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = FollowListPagination

    def get_queryset(self):
        user = self.request.user
        follows = user.follow.all()
        return [follow.following for follow in follows]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class FollowViewSet(viewsets.ModelViewSet):
    lookup_url_kwarg = 'user_id'
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def perform_create(self, serializer):
        user_id = self.kwargs.get(self.lookup_url_kwarg)
        following = get_object_or_404(CustomUser, id=int(user_id))
        user = self.request.user
        serializer.save(user=user, following=following)

    def destroy(self, request, user_id):
        following = get_object_or_404(CustomUser, id=int(user_id))
        user = self.request.user
        follow = get_object_or_404(Follow, user=user, following=following)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
