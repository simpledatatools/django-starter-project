from django.db import models
from django.db.models import JSONField

from django.conf import settings

from workspaces.models import *

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.SET_NULL, null=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    category_id  = models.CharField(max_length=16, null=False, blank=True)

    CATEGORY_STATUS = (
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    )
    
    status = models.CharField(
        max_length=25,
        choices=CATEGORY_STATUS,
        blank=False,
        default='active',
    )

    def __str__(self):
        return self.name


class Field(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    field_id  = models.CharField(max_length=16, null=False, blank=True)

    FIELD_TYPE = (
        ('text', 'Text'),
        ('number', 'Number'),
        ('Date', 'Date'),
        ('select', 'Select'),
        ('select-document', 'Select Document'),
    )

    type = models.CharField(
        max_length=25,
        choices=FIELD_TYPE,
        blank=False,
        default='active',
    )

    config = JSONField(null=True, blank=True)

    FIELD_STATUS = (
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    )

    status = models.CharField(
        max_length=25,
        choices=FIELD_STATUS,
        blank=False,
        default='active',
    )
    
    def __str__(self):
        return self.name


class Document(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    document_id  = models.CharField(max_length=16, null=False, blank=True)

    config = JSONField(null=True, blank=True)

    DOCUMENT_STATUS = (
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    )

    status = models.CharField(
        max_length=25,
        choices=DOCUMENT_STATUS,
        blank=False,
        default='active',
    )
    
    def __str__(self):
        return self.document_id
