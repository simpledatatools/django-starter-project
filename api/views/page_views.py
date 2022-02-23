from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from workspaces.models import Page
from api.serializers import PageSerializer

from rest_framework import status

from .permissions_check import *
from core.utils import randomstr


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createPage(request):
    user = request.user
    data = request.data

    if 'workspace_id' in data:
        workspace_id = data['workspace_id']
        # Verify the user has permission to be creating pages (only admins)
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            workspace = user_workspace['workspace']
            # Create the page
            try:

                page = Page.objects.create(
                    label=data['label'],
                    workspace=workspace,
                    page_id = randomstr(),
                    created_user=user,
                )

                serializer = PageSerializer(page, many=False)
                return Response(serializer.data)
    
            except Exception as e:
                print(e)
                message = {'detail': 'There was an error creating this page'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Field workspace_id is missing from the request'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getPages(request):
    user = request.user
    data = request.data

    if 'workspace_id' in data:
        workspace_id = data['workspace_id']
        # Verify the user has permission to be creating pages (only admins)
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            workspace = user_workspace['workspace']
            
            query = request.query_params.get('keyword')
            if query == None:
                query = ''

            pages = Page.objects.filter(
                workspace=workspace,
                label__icontains=query,
                status='active',
            ).order_by('label')

            page = request.query_params.get('page')
            paginator = Paginator(pages, 5)

            try:
                pages = paginator.page(page)
            except PageNotAnInteger:
                pages = paginator.page(1)
            except EmptyPage:
                pages = paginator.page(paginator.num_pages)

            if page == None:
                page = 1

            page = int(page)
            print('Page:', page)
            serializer = PageSerializer(pages, many=True)
            return Response({'pages': serializer.data, 'page': page, 'pages': paginator.num_pages})
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Field workspace_id is missing from the request'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getPage(request, page_id):

    user = request.user

    # Check if the page is valid
    page = Page.objects.filter(page_id=page_id, status='active').first()
    if page:
        workspace_id = page.workspace.workspace_id
        # Verify the user has permission for the page's workspace
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['user', 'admin'])
        if user_workspace['workspace']:
            
            serializer = PageSerializer(page, many=False)
            return Response({'pages': serializer.data})
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Page does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updatePage(request, page_id):
    data = request.data
    user = request.user

    # Check if the page is valid
    page = Page.objects.filter(page_id=page_id, status='active').first()
    if page:
        workspace_id = page.workspace.workspace_id
        # Verify the user has permission for the page's workspace and can edit
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            
            page.label = data['label']
            page.save()
            serializer = PageSerializer(page, many=False)
            return Response({'pages': serializer.data})
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Page does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def archivePage(request, page_id):
    
    user = request.user

    # Check if the page is valid
    page = Page.objects.filter(page_id=page_id, status='active').first()
    if page:
        workspace_id = page.workspace.workspace_id
        # Verify the user has permission for the page's workspace and can edit
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            page.status = 'archived'
            page.save()
            message = {'detail': 'Page was archived'}
            return Response(message, status=200)
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Page does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
