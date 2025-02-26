from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


ALLOWED_HOSTS = ['*']

# The URL part of the path (how browser requests it)
MEDIA_URL = '/photos/'

# The filesystem path (where Django looks for it)
MEDIA_ROOT = os.path.join(BASE_DIR, 'photos')
