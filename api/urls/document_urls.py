from django.urls import path
from api.views import document_views as views

urlpatterns = [
    
    path('', views.getDocuments, name="documents"),
    path('create/', views.createDocument, name="document-create"),
    path('<str:document_id>/', views.getDocument, name="document"),
    path('update/<str:document_id>/', views.updateDocument, name="document-update"),
    path('archive/<str:document_id>/', views.archiveDocument, name="document-archive"),
    
]