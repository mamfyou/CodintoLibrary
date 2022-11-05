from django_filters import FilterSet

from process.models import Request


class RequestFilter(FilterSet):
    class Meta:
        model = Request
        fields = {
            'type': ['exact'],
            'is_read': ['exact'],
            'created': ['gte', 'lte'],
        }
