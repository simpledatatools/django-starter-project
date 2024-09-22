from django.urls import path
from app.views import home as home
from app.views import items as items
from app.views import errors


urlpatterns = [
    
    path("home/", home.home, name="home"),

    path("error-403/", errors.error_403, name="error_403"),
    path("error-404/", errors.error_404, name="error_404"),
    path("error-500/", errors.error_500, name="error_500"),

    # Items
    path('items/', items.items, name='items'),
    path('items/add/', items.add_item, name='add_item'),
    path('items/<str:item_id>/', items.item_details, name='item_details'),
    path('items/edit/<str:item_id>/', items.edit_item, name='edit_item'),
    path('items/settings/<str:item_id>/', items.item_settings, name='item_settings'),
    path('fetch/items/', items.fetch_items, name='fetch_items'),
    path('fetch/items/add/', items.fetch_add_item, name='fetch_add_item'),
    path('fetch/items/<str:item_id>/', items.fetch_item_details, name='fetch_item_details'),
    path('fetch/items/edit/<str:item_id>/', items.fetch_edit_item, name='fetch_edit_item'),
    path('fetch/items/archive/<str:item_id>/', items.fetch_archive_item, name='fetch_archive_item'),

]
