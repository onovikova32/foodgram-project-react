from django.urls import path

from .views import FollowListViewSet, CustomUserViewSet, FollowViewSet

custom_user_viewset = CustomUserViewSet.as_view({'get': 'list',
                                                 'post': 'create'})

urlpatterns = [
    path('', custom_user_viewset, name='user_view'),
    path('subscriptions/', FollowListViewSet.as_view(), name='subscriptions'),
    path('<int:user_id>/subscribe/',
         FollowViewSet.as_view({'post': 'create',
                                'delete': 'destroy'}), name='subscribe')
]
