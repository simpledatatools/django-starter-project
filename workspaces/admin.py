from django.contrib import admin

from .models import *

class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'workspace_id', 'status']

admin.site.register(Workspace, WorkspaceAdmin)
