from celery.schedules import crontab

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend',
                                'rest_framework.filters.SearchFilter'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/minute',
        'user': '40/minute',
    }
}

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/1'
CELERY_BEAT_SCHEDULE = {
    'erase_notifications': {
        'task': 'process.tasks.erase_notifications',
        'schedule': crontab(hour='*/24'),
    },
    'time_warning_notification': {
        'task': 'process.tasks.time_warning_notification',
        'schedule': crontab(hour='*/24'),
    }
}