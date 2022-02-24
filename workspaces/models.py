from django.db import models
from django.db.models import JSONField

from django.conf import settings

class Workspace(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    workspace_id  = models.CharField(max_length=16, null=False, blank=True)

    WORKSPACE_STATUS = (
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    )
    
    status = models.CharField(
        max_length=25,
        choices=WORKSPACE_STATUS,
        blank=False,
        default='active',
    )

    def __str__(self):
        return self.name


class WorkspaceUser(models.Model):
    id = models.AutoField(primary_key=True)
    workspace = models.ForeignKey('Workspace', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    WORKSPACE_USER_STATUS = (
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    )

    status = models.CharField(
        max_length=25,
        choices=WORKSPACE_USER_STATUS,
        blank=False,
        default='active',
    )

    WORKSPACE_ROLE = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    role = models.CharField(
        max_length=25,
        choices=WORKSPACE_ROLE,
        blank=False,
        default='user',
    )

    def __str__(self):
        return self.id


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=200)
    workspace = models.ForeignKey('Workspace', on_delete=models.SET_NULL, null=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    tag_id  = models.CharField(max_length=16, null=False, blank=True)

    TAG_STATUS = (
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    )

    status = models.CharField(
        max_length=25,
        choices=TAG_STATUS,
        blank=False,
        default='active',
    )

    def __str__(self):
        return self.label


class Page(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.SET_NULL, null=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    page_slug = models.CharField(max_length=200, null=False, blank=False)
    page_id  = models.CharField(max_length=16, null=False, blank=True)
    
    PAGE_STATUS = (
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    )

    status = models.CharField(
        max_length=25,
        choices=PAGE_STATUS,
        blank=False,
        default='active',
    )

    def __str__(self):
        return self.title