from django_filters import rest_framework as filters

from reviews.models import Title


class TitleFilter(filters.FilterSet):
    """
    фильтруем произведения по названию, жанру, категории, году
    .../api/v1/titles/?category= (slug категории)
    .../api/v1/titles/?genre= (slug жанра)
    .../api/v1/titles/?name= (название, или его часть)
    .../api/v1/titles/?year= (год выпуска произведения)
    """
    name = filters.CharFilter(
        field_name='name', lookup_expr='icontains')
    year = filters.NumberFilter(field_name='year')
    category = filters.CharFilter(field_name='category__slug')
    genre = filters.CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ('name', 'genre', 'category', 'year',)
