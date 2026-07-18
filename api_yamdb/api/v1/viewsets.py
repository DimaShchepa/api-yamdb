from rest_framework.mixins import (ListModelMixin,
                                   CreateModelMixin,
                                   DestroyModelMixin)
from rest_framework import filters
from rest_framework.viewsets import GenericViewSet


class CategoryGenreViewSet(ListModelMixin,
                           CreateModelMixin,
                           DestroyModelMixin,
                           GenericViewSet):
    """Provide common API behavior for categories and genres."""

    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
