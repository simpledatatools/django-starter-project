import datetime
from django.db import models
from django.conf import settings
from files.models import *
from accounts.models import *
from files.storage_config import *
from core.utils import *
from channels.layers import get_channel_layer 
from asgiref.sync import async_to_sync

from rest_framework_api_key.models import AbstractAPIKey


# ====================================================================================================
# Items
# ====================================================================================================

class Item(models.Model):
    id = models.CharField(max_length=32, primary_key=True, default=generate_model_id, editable=False)
    item_id = models.CharField(editable=False, max_length=32, null=True)
    name = models.CharField(max_length=250)
    cover_photo = models.ForeignKey('files.File', on_delete=models.SET_NULL, null=True)
    item_settings = models.JSONField(default=dict)
    status = models.CharField(max_length=20, default='active')
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    STATUS = (
        ('active', 'Active'),
        ('archived', 'Archived'),
    )

    status = models.CharField(
        max_length=25,
        choices=STATUS,
        blank=False,
        default='active',
    )
    
    def __str__(self):
        return self.id

    class Meta:
        indexes = [
            models.Index(fields=['item_id'], name='item_index'),
        ]