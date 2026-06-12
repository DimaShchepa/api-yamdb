from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, signup, token


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/signup/', signup, name='signup'),
    path('auth/token/', token, name='token'),
    path('', include(router.urls)),
]
