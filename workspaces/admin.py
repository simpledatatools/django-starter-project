from django.contrib import admin

from core.utils import randomstr

from .models import *

class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'workspace_id', 'status']
    fields = ['name', 'status', 'workspace_id', 'created_user', 'created_at', 'last_updated']
    readonly_fields = ['workspace_id', 'created_user', 'created_at', 'last_updated']
    search_fields = ('name', 'workspace_id')
    list_per_page = 50

    # Adds the public id and created user before saving
    def save_model(self, request, obj, form, change):
        if obj.workspace_id == None or obj.workspace_id == '':
            obj.workspace_id = randomstr()
        if obj.created_user == None:
            obj.created_user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Workspace, WorkspaceAdmin)


class PageAdmin(admin.ModelAdmin):
    list_display = ['label', 'page_slug', 'workspace', 'page_id', 'status']
    fields = ['workspace', 'label', 'page_slug', 'status', 'page_id', 'created_user', 'created_at', 'last_updated']
    readonly_fields = ['page_id', 'created_user', 'created_at', 'last_updated']
    search_fields = ('label', 'page_id', 'page_slug')
    list_per_page = 50

    # Adds the public id and created user before saving
    def save_model(self, request, obj, form, change):
        if obj.page_id == None or obj.page_id == '':
            obj.page_id = randomstr()
        if obj.created_user == None:
            obj.created_user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Page, PageAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = ['label', 'workspace', 'tag_id', 'status']
    fields = ['workspace', 'label', 'status', 'tag_id', 'created_user', 'created_at', 'last_updated']
    readonly_fields = ['tag_id', 'created_user', 'created_at', 'last_updated']
    search_fields = ('label', 'tag_id')
    list_per_page = 50

    # Adds the public id and created user before saving
    def save_model(self, request, obj, form, change):
        if obj.tag_id == None or obj.tag_id == '':
            obj.tag_id = randomstr()
        if obj.created_user == None:
            obj.created_user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Tag, TagAdmin)