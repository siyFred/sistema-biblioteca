import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name='genre', lookup_expr='icontains')
    author = django_filters.CharFilter(field_name='author', lookup_expr='icontains')
    available = django_filters.BooleanFilter(field_name='available_copies', method='filter_available')

    class Meta:
        model = Book
        fields = ['genre', 'author', 'available']

    def filter_available(self, queryset, name, value):
        if value:
            return queryset.filter(available_copies__gt=0)
        return queryset
import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(lookup_expr='icontains')
    language = django_filters.CharFilter(lookup_expr='icontains')

    min_year = django_filters.NumberFilter(field_name='publication_date', lookup_expr='year__gte')
    max_year = django_filters.NumberFilter(field_name='publication_date', lookup_expr='year__lte')

    available = django_filters.BooleanFilter(method='filter_available')

    class Meta:
        model = Book
        fields = ['genre', 'language', 'publisher']

    def filter_available(self, queryset, name, value):
        if value:
            return queryset.filter(available_copies__gt=0)
        return queryset
