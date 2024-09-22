from django.urls import path
from api.views import item_views as views

urlpatterns = [
    path("", views.get_items, name="api_items"),
    path("count/", views.get_item_count, name="api_items_count"),
    path("add/", views.add_item, name="api_add_item"),
    path("add/bulk/", views.add_items, name="api_add_items"),
    path("update/bulk/", views.update_items, name="api_update_items"),
    path("archive/bulk/", views.archive_items, name="api_archive_items"),
    path("<str:item_id>/", views.get_item, name="api_item"),
    path("<str:item_id>/update/",views.update_item, name="api_update_item"),
    path("<str:item_id>/archive/",views.archive_item, name="api_archive_item"),
]
