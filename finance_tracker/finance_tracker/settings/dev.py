from .base import *
DEBUG = True

DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000

# Use in-memory broker for Celery
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_STORE_EAGER_RESULT = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_RESULT_EXPIRES = 3600  # e.g., results expire after 1 hour

CELERY_CACHE_BACKEND = 'django.core.cache.backends.locmem.LocMemCache'
CELERY_CACHE_LOCATION = ''  # This can be left blank for LocMemCache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
