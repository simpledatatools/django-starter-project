from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from workspaces.models import Workspace, WorkspaceUser
from api.serializers import WorkspaceSerializer

from rest_framework import status

from .permissions_check import *
from core.utils import randomstr


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createWorkspace(request):
    user = request.user
    data = request.data

    try:

        # Create the workspace
        workspace = Workspace.objects.create(
            name=data['name'],
            workspace_id = randomstr(),
            created_user=user,
        )

        serializer = WorkspaceSerializer(workspace, many=False)
        return Response(serializer.data)
    
    except Exception as e:
        print(e)
        message = {'detail': 'There was an error creating this workspace'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getWorkspaces(request):

    user = request.user
    
    # Get the workspaces the user is added to
    workspace_relations = WorkspaceUser.objects.filter(
        user=user,
        status='active',
    )

    # Create array of valid workspace ids for the user
    workspace_ids = []
    for workspace_relation in workspace_relations:
        workspace_ids.append(workspace_relation.workspace.id)

    query = request.query_params.get('keyword')
    if query == None:
        query = ''

    workspaces = Workspace.objects.filter(
        id__in=workspace_ids,
        name__icontains=query,
        status='active',
    ).order_by('name')

    page = request.query_params.get('page')
    paginator = Paginator(workspaces, 5)

    try:
        workspaces = paginator.page(page)
    except PageNotAnInteger:
        workspaces = paginator.page(1)
    except EmptyPage:
        workspaces = paginator.page(paginator.num_pages)

    if page == None:
        page = 1

    page = int(page)
    print('Page:', page)
    serializer = WorkspaceSerializer(workspaces, many=True)
    return Response({'workspaces': serializer.data, 'page': page, 'pages': paginator.num_pages})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getWorkspace(request, workspace_id):

    user = request.user
    user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['user', 'admin'])
    if user_workspace['workspace']:
        serializer = WorkspaceSerializer(user_workspace['workspace'], many=False)
        return Response(serializer.data)
    else:
        message = {'detail': user_workspace['message']}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
       

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateWorkspace(request, workspace_id):
    data = request.data
    user = request.user
    user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
    if user_workspace['workspace']:
        workspace = user_workspace['workspace']
        workspace.name = data['name']
        workspace.save()
        serializer = WorkspaceSerializer(workspace, many=False)
        return Response(serializer.data)
    else:
        message = {'detail': user_workspace['message']}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def archiveWorkspace(request, workspace_id):
    user = request.user
    user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
    if user_workspace['workspace']:
        workspace = user_workspace['workspace']
        workspace.status = 'archived'
        workspace.save()
        message = {'detail': 'Workspace was archived'}
        return Response(message, status=200)
    else:
        message = {'detail': user_workspace['message']}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

