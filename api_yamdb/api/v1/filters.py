import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )
    year = django_filters.NumberFilter(field_name='year', lookup_expr='exact')
    category = django_filters.CharFilter(field_name='category__slug')
    genre = django_filters.CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ['name', 'year', 'category', 'genre']

    @property
    def qs(self):
        return super().qs.distinct()
