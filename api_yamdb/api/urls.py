from django.urls import path, include
from rest_framework import routers

from .views import (TitleViewSet, GenreViewSet, CategoryViewSet,
                    ReviewViewSet, CommentViewSet, UserViewSet)

router = routers.DefaultRouter()
router.register('titles', TitleViewSet, basename='titles')
router.register(r'titles/(?P<titles_id>\d+)/comments',
                CommentViewSet, basename='comments')
router.register(r'titles/(?P<titles_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')

urlpatterns = [
    path('', include(router.urls)),
]