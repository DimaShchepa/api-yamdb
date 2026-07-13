from rest_framework.mixins import (ListModelMixin,
                                   CreateModelMixin,
                                   DestroyModelMixin)
from rest_framework.viewsets import GenericViewSet
from rest_framework import filters


class SlugLookupMixin:
    """Миксин, который устанавливает поиск по slug для lookup_field."""
    lookup_field = 'slug'


class SearchFilterMixin:
    """Миксин с настройками фильтров для справочников."""
    filter_backends = (filters.SearchFilter,)
    search_fields = ['name']


class ReadOnlyListCreateDestroyViewSet(SlugLookupMixin,
                                       SearchFilterMixin,
                                       ListModelMixin,
                                       CreateModelMixin,
                                       DestroyModelMixin,
                                       GenericViewSet):
    pass
