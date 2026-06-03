from django.urls import path, include
from rest_framework import routers

from .views import (TitleViewSet, GenreViewSet, CategoryViewSet,
                    ReviewViewSet, CommentViewSet, UserViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(r'titles/(?P<titles_id>\d+)/comments',
                   CommentViewSet, basename='comments')
router_v1.register(r'titles/(?P<titles_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
