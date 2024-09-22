from __future__ import absolute_import, unicode_literals
import os
from .base import *

import colorlog
import logging

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

import dj_database_url

DATABASES["default"] = dj_database_url.config()

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = [os.environ["HOST_URL"], os.environ["ACCESS_URL"]]

# Redirect to https in production
SECURE_SSL_REDIRECT = True
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
AWS_S3_REGION = os.environ["AWS_S3_REGION_NAME"]
AWS_S3_CUSTOM_DOMAIN = "s3.{}.amazonaws.com/{}".format(
    AWS_S3_REGION, AWS_STORAGE_BUCKET_NAME
)
AWS_S3_HOST = "s3.{}.amazonaws.com".format(AWS_S3_REGION)

DEFAULT_FILE_STORAGE = "files.storage_config.PublicMediaStorage"
# The absolute path to the directory where collectstatic will collect static files for deployment.
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
# The URL to use when referring to static files (where they will be served from)
STATIC_URL = "/static/"

AWS_PUBLIC_MEDIA_LOCATION = "media"
AWS_PRIVATE_MEDIA_LOCATION = "private"
MEDIA_URL = "https://{}/{}/".format(AWS_S3_CUSTOM_DOMAIN, AWS_PUBLIC_MEDIA_LOCATION)
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
PRIVATE_FILE_STORAGE = "files.storage_config.PrivateMediaStorage"

DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 10MB limit

# CELERY STUFF
REDIS_URL = os.environ["REDIS_URL"]
BROKER_URL = os.environ["REDIS_URL"]
CELERY_RESULT_BACKEND = os.environ["REDIS_URL"]

EMAIL_HOST = os.environ["EMAIL_HOST"]
EMAIL_PORT = os.environ["EMAIL_PORT"]
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
EMAIL_USE_TLS = os.environ["EMAIL_USE_TLS"]
BASE_URL = os.environ["BASE_URL"]

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.environ.get('REDIS_URL')],
        },
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(levelname)s: %(message)s',
            'log_colors': {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Ensure print statements and other outputs are captured
logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])

LIVE = os.environ["LIVE"]
