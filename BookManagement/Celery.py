import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BookManagement.settings')
celery_obj = Celery('BookManagement')
celery_obj.config_from_object('django.conf:settings', namespace='CELERY')
celery_obj.autodiscover_tasks()
