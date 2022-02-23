from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from workspaces.models import Tag
from api.serializers import TagSerializer

from rest_framework import status

from .permissions_check import *


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createTag(request):
    user = request.user
    data = request.data

    if 'workspace_id' in data:
        workspace_id = data['workspace_id']
        # Verify the user has permission to be creating tags (only admins)
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            workspace = user_workspace['workspace']
            # Create the tag
            try:

                tag = Tag.objects.create(
                    label=data['label'],
                    workspace=workspace,
                    created_user=user,
                )

                serializer = TagSerializer(tag, many=False)
                return Response(serializer.data)
    
            except Exception as e:
                print(e)
                message = {'detail': 'There was an error creating this tag'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Field workspace_id is missing from the request'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getTags(request):
    user = request.user
    data = request.data

    if 'workspace_id' in data:
        workspace_id = data['workspace_id']
        # Verify the user has permission to be creating tags (only admins)
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            workspace = user_workspace['workspace']
            
            query = request.query_params.get('keyword')
            if query == None:
                query = ''

            tags = Tag.objects.filter(
                workspace=workspace,
                label__icontains=query,
                status='active',
            ).order_by('label')

            page = request.query_params.get('page')
            paginator = Paginator(tags, 5)

            try:
                tags = paginator.page(page)
            except PageNotAnInteger:
                tags = paginator.page(1)
            except EmptyPage:
                tags = paginator.page(paginator.num_pages)

            if page == None:
                page = 1

            page = int(page)
            print('Page:', page)
            serializer = TagSerializer(tags, many=True)
            return Response({'tags': serializer.data, 'page': page, 'pages': paginator.num_pages})
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Field workspace_id is missing from the request'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getTag(request, tag_id):

    user = request.user

    # Check if the tag is valid
    tag = Tag.objects.filter(tag_id=tag_id, status='active').first()
    if tag:
        workspace_id = tag.workspace.workspace_id
        # Verify the user has permission for the tag's workspace
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['user', 'admin'])
        if user_workspace['workspace']:
            
            serializer = TagSerializer(tag, many=False)
            return Response({'tags': serializer.data})
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Tag does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateTag(request, tag_id):
    data = request.data
    user = request.user

    # Check if the tag is valid
    tag = Tag.objects.filter(tag_id=tag_id, status='active').first()
    if tag:
        workspace_id = tag.workspace.workspace_id
        # Verify the user has permission for the tag's workspace and can edit
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            
            tag.label = data['label']
            tag.save()
            serializer = TagSerializer(tag, many=False)
            return Response({'tags': serializer.data})
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Tag does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def archiveTag(request, tag_id):
    
    user = request.user

    # Check if the tag is valid
    tag = Tag.objects.filter(tag_id=tag_id, status='active').first()
    if tag:
        workspace_id = tag.workspace.workspace_id
        # Verify the user has permission for the tag's workspace and can edit
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            tag.status = 'archived'
            tag.save()
            message = {'detail': 'Tag was archived'}
            return Response(message, status=200)
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Tag does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
