from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug Toolbar
try:
    import debug_toolbar
    INSTALLED_APPS = list(INSTALLED_APPS) + ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + list(MIDDLEWARE)
    INTERNAL_IPS = ['127.0.0.1']
except ImportError:
    pass