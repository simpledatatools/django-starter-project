from django.db.models.signals import pre_save
from .models import *
from core.utils import randomstr


def initCategory(sender, instance, **kwargs):
    category = instance
    # On init, add the other ids
    if category.category_id == None:
        category.category_id = randomstr()
pre_save.connect(initCategory, sender=Category)


def initField(sender, instance, **kwargs):
    field = instance
    # On init, add the other ids
    if field.field_id == None:
        field.field_id = randomstr()
pre_save.connect(initField, sender=Field)


def initDocument(sender, instance, **kwargs):
    document = instance
    # On init, add the other ids
    if document.document_id == None:
        document.document_id = randomstr()
pre_save.connect(initDocument, sender=Document)