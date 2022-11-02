from django_filters import rest_framework, BooleanFilter, ChoiceFilter
from books.models import Book, Comment
from process.models import Notification


class CommentPanelFilter(rest_framework.FilterSet):
    #
    class Meta:
        model = Comment
        fields = {
            'created_at': ['lte', 'gte'],
        }


class NotificationPanel(rest_framework.FilterSet):
    my_notif = ChoiceFilter(field_name='type', method='my_notif_filter', choices=[('me', 'me'), ('general', 'general')])

    def my_notif_filter(self, queryset, value, *args, **kwargs):
        print(value)
        print(args)
        print(len(args))
        if len(args) == 1 and args[0] == 'me':
            return queryset.filter(type__in=['BR', 'CM', 'EX', 'RT', 'TW', 'AV'])
        elif len(args) == 1 and args[0] == 'general':
            return queryset.filter(type='GN')
        else:
            return queryset
