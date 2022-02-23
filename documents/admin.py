from django.contrib import admin

from core.utils import randomstr

from .models import *

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_id', 'workspace', 'status']
    fields = ['workspace', 'name', 'status', 'category_id', 'created_user', 'created_at', 'last_updated']
    readonly_fields = ['category_id', 'created_user', 'created_at', 'last_updated']
    search_fields = ('name', 'category_id')
    list_per_page = 50

    # Adds the public id and created user before saving
    def save_model(self, request, obj, form, change):
        if obj.category_id == None or obj.category_id == '':
            obj.category_id = randomstr()
        if obj.created_user == None:
            obj.created_user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Category, CategoryAdmin)

class FieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'category', 'field_id', 'status']
    fields = ['category', 'name', 'type', 'status', 'field_id', 'created_user', 'created_at', 'last_updated']
    readonly_fields = ['field_id', 'created_user', 'created_at', 'last_updated']
    search_fields = ('name', 'field_id')
    list_per_page = 50

    # Adds the public id and created user before saving
    def save_model(self, request, obj, form, change):
        if obj.field_id == None or obj.field_id == '':
            obj.field_id = randomstr()
        if obj.created_user == None:
            obj.created_user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Field, FieldAdmin)

class DocumentAdmin(admin.ModelAdmin):
    list_display = ['document_id', 'category', 'status']
    fields = ['category', 'status', 'document_id', 'created_user', 'created_at', 'last_updated']
    readonly_fields = ['document_id', 'created_user', 'created_at', 'last_updated']
    search_fields = ('document_id',)
    list_per_page = 50

    # Adds the public id and created user before saving
    def save_model(self, request, obj, form, change):
        if obj.document_id == None or obj.document_id == '':
            obj.document_id = randomstr()
        if obj.created_user == None:
            obj.created_user = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Document, DocumentAdmin)