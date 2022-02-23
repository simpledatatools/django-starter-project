from django.urls import path
from api.views import category_views as views

urlpatterns = [
    
    path('', views.getCategories, name="categories"),
    path('create/', views.createCategory, name="category-create"),
    path('<str:category_id>/', views.getCategory, name="category"),
    path('update/<str:category_id>/', views.updateCategory, name="category-update"),
    path('archive/<str:category_id>/', views.archiveCategory, name="category-archive"),
    
]