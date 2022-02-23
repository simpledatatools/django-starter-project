from django.contrib import admin

from .models import *

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category_id', 'workspace', 'status']

admin.site.register(Category, CategoryAdmin)

class FieldAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type', 'field_id', 'category', 'status']

admin.site.register(Field, FieldAdmin)

class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'document_id', 'category', 'status']

admin.site.register(Document, DocumentAdmin)