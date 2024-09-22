from django.contrib import admin

from .models import *
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):

    model = CustomUser

    fieldsets = (*UserAdmin.fieldsets,)
    list_display = (
        "id",
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    search_fields = (
        "first_name",
        "last_name",
        "username",
        "email",
    )
    list_filter = ("is_staff",)

    # def has_delete_permission(self, request, obj=None):
    #     return False

    # def has_add_permission(self, request, obj=None):
    #     return False

    # def has_change_permission(self, request, obj=None):
    #     return False


admin.site.register(CustomUser, CustomUserAdmin)
