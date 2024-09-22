from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid

from files.models import *
from backend.models import *
from core.utils import *


class CustomUser(AbstractUser):
    pass
    # add additional fields in here
    user_extras = models.ForeignKey("UserExtras", on_delete=models.SET_NULL, null=True)
    display_name = models.CharField(max_length=250, null=True, blank=True)
    profile_photo = models.ForeignKey(
        "files.File", on_delete=models.SET_NULL, null=True
    )
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class UserExtras(models.Model):
    id = models.CharField(
        max_length=32, primary_key=True, default=generate_model_id, editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    last_active = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "User Extras"
        verbose_name_plural = "User Extras"


class UserPasscode(models.Model):
    id = models.CharField(
        max_length=32, primary_key=True, default=generate_model_id, editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    passcode = models.CharField(
        max_length=64, editable=False
    )
    name = models.CharField(max_length=255, null=True)
    view_summary = models.BooleanField(default=True)
    view_live = models.BooleanField(default=True)
    view_history = models.BooleanField(default=True)
    view_checkins = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    status = models.CharField(
        max_length=10, default="active"
    ) 

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "User Passcodes"
        verbose_name_plural = "User Passcodes"


class MailLinkModel(models.Model):
    id = models.CharField(
        max_length=32, primary_key=True, default=generate_model_id, editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    key = models.CharField(max_length=255, default="", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_delete = models.BooleanField(default=False, null=True, blank=True)
    new_email = models.EmailField(null=True, blank=True)

    link_type_choices = (
        ('register', 'Register'),
        ('reset_password', 'Reset Password'),
        ('password_change', 'Password Change'),
        ('email_change', 'Email Change'),
    )

    link_type = models.CharField(
        max_length=100, default="", choices=link_type_choices, null=True, blank=True
    )

    def __str__(self):
        return self.key


class VerifyCode(models.Model):
    id = models.CharField(
        max_length=32, primary_key=True, default=generate_model_id, editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    code = models.CharField(max_length=5, null=True, blank=True)
    key = models.CharField(max_length=64, null=True, blank=True)
    email = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, default="pending", null=True, blank=True)

    code_type_choices = (
        ('register', 'Register'),
        ('reset_password', 'Reset Password'),
        ('password_change', 'Password Change'),
        ('email_change', 'Email Change'),
    )

    code_type = models.CharField(
        max_length=100, default="", choices=code_type_choices, null=True, blank=True
    )

    def __str__(self):
        return self.id
