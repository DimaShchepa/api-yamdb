from django.urls import include, path
from rest_framework import routers

from .views import (TitleViewSet, GenreViewSet, CategoryViewSet,
                    ReviewViewSet, CommentViewSet, UserViewSet,
                    signup, token)

router = routers.DefaultRouter()
router.register('titles', TitleViewSet, basename='titles')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', signup, name='signup'),
    path('auth/token/', token, name='token'),
]
