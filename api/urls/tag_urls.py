from django.urls import path
from api.views import tag_views as views

urlpatterns = [
    
    path('', views.getTags, name="tags"),
    path('create/', views.createTag, name="tag-create"),
    path('<str:tag_id>/', views.getTag, name="tag"),
    path('update/<str:tag_id>/', views.updateTag, name="tag-update"),
    path('archive/<str:tag_id>/', views.archiveTag, name="tag-archive"),
    
]