from django_filters import FilterSet

from process.models import Request, History, Notification


class RequestFilter(FilterSet):
    class Meta:
        model = Request
        fields = {
            'type': ['exact'],
            'is_read': ['exact'],
            'created': ['gte', 'lte'],
        }


class HistoryFilter(FilterSet):
    class Meta:
        model = History
        fields = {
            'created': ['gte', 'lte'],
        }


class NotificationFilter(FilterSet):
    class Meta:
        model = Notification
        fields = {
            'created': ['gte', 'lte'],
        }
