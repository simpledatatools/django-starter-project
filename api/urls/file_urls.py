from django.urls import path
from api.views import file_views as views


urlpatterns = [
    path("sign-files/", views.api_file_sign, name="api_sign_files"),
]
