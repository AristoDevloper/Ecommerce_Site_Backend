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
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB-NAME', 'postgres'),
        'USER': os.getenv('DB-USER', 'postgres'),
        'PASSWORD': os.getenv('DB-PASSWORD', 'postgres'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Channel layer configuration for chat app
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', '0')
REDIS_SOCKET_TIMEOUT = os.getenv('REDIS_SOCKET_TIMEOUT', '10')
REDIS_SOCKET_CONNECT_TIMEOUT = os.getenv('REDIS_SOCKET_CONNECT_TIMEOUT', '10')

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [
                f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}?socket_timeout={REDIS_SOCKET_TIMEOUT}&socket_connect_timeout={REDIS_SOCKET_CONNECT_TIMEOUT}'
            ],
        },
    }
}
