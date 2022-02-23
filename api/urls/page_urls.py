from django.urls import path
from api.views import page_views as views

urlpatterns = [
    
    path('', views.getPages, name="pages"),
    path('create/', views.createPage, name="page-create"),
    path('<str:page_id>/', views.getPage, name="page"),
    path('update/<str:page_id>/', views.updatePage, name="page-update"),
    path('archive/<str:page_id>/', views.archivePage, name="page-archive"),
    
]