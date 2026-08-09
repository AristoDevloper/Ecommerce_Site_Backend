from .base import *
import os
import dj_database_url

DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

CORS_ALLOW_CREDENTIALS = True

# Database
# For local, you might be using SQLite or a local Postgres. Let's use SQLite as fallback or the one from env
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600,  
        ssl_require=False
    ),
    # {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
}

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
