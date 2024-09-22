from django.urls import path
from website.views import website as website
from website.views import items as items
from website.views import errors


urlpatterns = [

    path("", website.landing, name="landing"),
    path("terms/", website.terms, name="terms"),
    path("privacy/", website.privacy, name="privacy"),
    path("about/", website.about, name="about"),

    path("error-403/", errors.error_403, name="error_403"),
    path("error-404/", errors.error_404, name="error_404"),
    path("error-500/", errors.error_500, name="error_500"),

    # Items
    path('items/', items.items, name='website_items'),
    path('items/<str:item_id>/', items.item_details, name='website_item_details'),
    path('fetch/items/', items.fetch_items, name='website_fetch_items'),
    path('fetch/items/<str:item_id>/', items.fetch_item_details, name='website_fetch_item_details'),

]
