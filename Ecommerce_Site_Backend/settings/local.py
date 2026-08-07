from .base import *
import os

DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

CORS_ALLOW_CREDENTIALS = True

# Database
# For local, you might be using SQLite or a local Postgres. Let's use SQLite as fallback or the one from env
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Channel layer configuration for chat app
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', '0')
REDIS_SOCKET_TIMEOUT = os.getenv('REDIS_SOCKET_TIMEOUT', '5')
REDIS_SOCKET_CONNECT_TIMEOUT = os.getenv('REDIS_SOCKET_CONNECT_TIMEOUT', '5')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'daphne.channels.RedisChannelLayer',
        'CONFIG': {
            'hosts': [
                f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}?socket_timeout={REDIS_SOCKET_TIMEOUT}&socket_connect_timeout={REDIS_SOCKET_CONNECT_TIMEOUT}'
            ],
        },
    }
}
