from django.urls import path
from api.views import workspace_views as views

urlpatterns = [

    path('', views.getWorkspaces, name="workspaces"),
    path('create/', views.createWorkspace, name="workspace-create"),
    path('<str:workspace_id>/', views.getWorkspace, name="workspace"),
    path('update/<str:workspace_id>/', views.updateWorkspace, name="workspace-update"),
    path('archive/<str:workspace_id>/', views.archiveWorkspace, name="workspace-archive"),

]