from __future__ import absolute_import
import os
from celery import Celery

# Setup django and celery to work with tasks and models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
app = Celery("core")
app.config_from_object("django.conf:settings")

# ------------------------------------------------------------------------------
