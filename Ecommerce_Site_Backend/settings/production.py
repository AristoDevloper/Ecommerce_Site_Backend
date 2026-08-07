from .base import *
import os
import dj_database_url

DEBUG = False

# Example: should be loaded from env
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', ['ecommercesitebackend02-gtmb1xvrg-aristodev-team.vercel.app',"ecommercesitebackend02-hsr81i725-aristodev-team.vercel.app"]).split(',')

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# In production, use a real email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Channel layer configuration for chat app
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', '0')
REDIS_SOCKET_TIMEOUT = os.getenv('REDIS_SOCKET_TIMEOUT', '5')
REDIS_SOCKET_CONNECT_TIMEOUT = os.getenv('REDIS_SOCKET_CONNECT_TIMEOUT', '5')

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

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
