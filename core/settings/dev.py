from .base import *
from dotenv import load_dotenv

load_dotenv()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "p6_izlna_zfupnk57int)z2cew$qs7=q(hkm)f^1xhc%5pyurr"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

# These are just for dev, for prod always use environ vars!
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_STORAGE_BUCKET_NAME = os.environ["AWS_STORAGE_BUCKET_NAME"]
AWS_S3_REGION = os.environ["AWS_S3_REGION_NAME"]
AWS_S3_CUSTOM_DOMAIN = "s3.{}.amazonaws.com/{}".format(
    AWS_S3_REGION, AWS_STORAGE_BUCKET_NAME
)
AWS_S3_HOST = "s3.{}.amazonaws.com".format(AWS_S3_REGION)

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
# The absolute path to the directory where collectstatic will collect static files for deployment.
STATIC_ROOT = os.path.join(BASE_DIR, "static")
# The URL to use when referring to static files (where they will be served from)
STATIC_URL = "/static/"

# s3 private media settings
AWS_PUBLIC_MEDIA_LOCATION = "media"
AWS_PRIVATE_MEDIA_LOCATION = "private"
MEDIA_URL = "https://{}/{}/".format(AWS_S3_CUSTOM_DOMAIN, AWS_PUBLIC_MEDIA_LOCATION)
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

DEFAULT_FILE_STORAGE = "files.storage_config.PublicMediaStorage"
PRIVATE_FILE_STORAGE = "files.storage_config.PrivateMediaStorage"

# Email stuff
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = "testing@example.com"
BASE_URL = "http://127.0.0.1:8000/"

# CELERY STUFF
REDIS_URL = "redis://localhost:6379"
BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Africa/Nairobi"

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

FRONTEND_URL = 'http://localhost:3000'

LIVE = "True"
