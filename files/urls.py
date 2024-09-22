from django.urls import path
from . import views

urlpatterns = [
    path("ajax/file/sign/", views.fetch_file_sign, name="fetch_file_sign"),
]
