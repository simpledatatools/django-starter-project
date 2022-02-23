from django.urls import path
from api.views import field_views as views

urlpatterns = [
    
    path('', views.getFields, name="fields"),
    path('create/', views.createField, name="field-create"),
    path('<str:field_id>/', views.getField, name="field"),
    path('update/<str:field_id>/', views.updateField, name="field-update"),
    path('archive/<str:field_id>/', views.archiveField, name="field-archive"),
    
]