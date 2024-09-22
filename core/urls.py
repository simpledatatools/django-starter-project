from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from .views import robots_txt
from app.views import errors as errors

handler500 = errors.error_500
handler403 = errors.error_403
handler404 = errors.error_404
handler401 = errors.error_401


urlpatterns = [
    
    # Templates and core routes
    path("internal/", admin.site.urls),  # Standard django admin app
    path("", include("accounts.urls")),  # App for managing accounts
    path("", include("website.urls")),
    path("admin/", include("app.urls")),
    path("files/", include("files.urls")),
    
    # API Documentation
    path('api/', SpectacularAPIView.as_view(), name='schema'),  # Schema generation
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # Swagger UI
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # ReDoc UI
    
    # API
    path("api/users/", include("api.urls.user_urls")),
    path("api/files/", include("api.urls.file_urls")),
    path("api/items/", include("api.urls.item_urls")),
    
    # SEO Stuff
    path("robots.txt", robots_txt),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Django Starter Project Admin Panel"
admin.site.site_title = "Django Starter Project Admin Panel"
admin.site.index_title = ""
