from django.db import models
from .storage_config import *
from core.utils import *

class File(models.Model):
    id = models.CharField(
        max_length=32, primary_key=True, default=generate_model_id, editable=False
    )
    legacy_id = models.IntegerField(null=True)
    display_id = models.CharField(editable=False, max_length=16, null=False)
    file = models.FileField(upload_to="uploads/", storage=PrivateMediaStorage())
    thumbnail = models.FileField(
        upload_to="uploads/", storage=PrivateMediaStorage(), null=True
    )
    micro_thumbnail = models.FileField(
        upload_to="uploads/", storage=PrivateMediaStorage(), null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    file_name = models.CharField(max_length=250, null=True)
    original_name = models.CharField(max_length=250, null=True)
    display_name = models.CharField(max_length=250, null=True)
    file_size = models.IntegerField(null=True)
    file_size_mb = models.FloatField(null=True)
    file_type = models.CharField(max_length=250, null=True)
    file_extension = models.CharField(max_length=25, null=True)
    file_display_type = models.CharField(max_length=25, null=True)
    data = models.JSONField(null=True)

    FILE_STATUS = (
        ("active", "Active"),
        ("archived", "Archived"),
    )

    status = models.CharField(
        max_length=25,
        choices=FILE_STATUS,
        blank=False,
        default="active",
    )
