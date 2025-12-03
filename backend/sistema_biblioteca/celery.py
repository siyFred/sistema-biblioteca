import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_biblioteca.settings')

celery = Celery('sistema_biblioteca')
celery.config_from_object('django.conf:settings', namespace='CELERY')
celery.autodiscover_tasks()