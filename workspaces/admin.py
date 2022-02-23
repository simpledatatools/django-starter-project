from django.contrib import admin

from .models import *

class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'workspace_id', 'status']
    fields = ['name', 'status']

admin.site.register(Workspace, WorkspaceAdmin)

class PageAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'page_id', 'page_slug', 'workspace', 'status']
    fields = ['workspace', 'label', 'page_slug', 'status']

admin.site.register(Page, PageAdmin)

class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'tag_id', 'workspace', 'status']
    fields = ['workspace', 'label', 'status']

admin.site.register(Tag, TagAdmin)