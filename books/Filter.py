import django_filters
from django.db.models import Avg

from books.models import Book, Rate


class BookFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Book
        fields = ['category']

    is_available = django_filters.BooleanFilter(field_name='count',
                                                lookup_expr='exact',
                                                method='filter_is_available')
    most_wanted = django_filters.BooleanFilter(field_name='wanted_to_read',
                                               lookup_expr='exact',
                                               method='filter_most_wanted')
    new = django_filters.BooleanFilter(field_name='created_at',
                                       lookup_expr='exact',
                                       method='filter_new')
    most_popular = django_filters.BooleanFilter(field_name='bookRate',
                                                lookup_expr='exact',
                                                method='filter_most_popular')

    def filter_is_available(self, queryset, data, value):
        if value is True:
            return queryset.filter(count__gt=0)
        return queryset

    def filter_most_wanted(self, queryset, data, value):
        if value is True:
            return queryset.order_by('-wanted_to_read')
        return queryset

    def filter_new(self, queryset, data, value):
        if value is True:
            return queryset.order_by('-created_at')
        return queryset

    def filter_most_popular(self, queryset, data, value):
        if value is True:
            return queryset.annotate(avg_rate=Avg('bookRate__rate')).order_by('-avg_rate')
        return queryset
