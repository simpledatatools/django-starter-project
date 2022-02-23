from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from documents.models import Field
from api.serializers import FieldSerializer

from rest_framework import status

from .permissions_check import *
from core.utils import randomstr


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createField(request):
    user = request.user
    data = request.data

    if 'category_id' in data:
        category_id = data['category_id']

        category = Category.objects.filter(category_id=category_id, status='active').first()
        if category:
           
            workspace_id = category.workspace.workspace_id
            # Verify the user has permission to be creating fields (only admins)
            user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
            if user_workspace['workspace']:
                workspace = user_workspace['workspace']
                # Create the field
                try:

                    field = Field.objects.create(
                        name=data['name'],
                        type=data['type'],
                        category=category,
                        field_id = randomstr(),
                        created_user=user,
                    )
                    
                    if 'config' in data:
                        field.config=data['config']
                        field.save()

                    serializer = FieldSerializer(field, many=False)
                    return Response(serializer.data)
        
                except Exception as e:
                    print(e)
                    message = {'detail': 'There was an error creating this field'}
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                message = {'detail': user_workspace['message']}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)

        else:
            message = {'detail': 'Category does not exist'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Field category_id is missing from the request'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getFields(request):
    user = request.user
    data = request.data

    if 'category_id' in data:
        category_id = data['category_id']

        category = Category.objects.filter(category_id=category_id, status='active').first()
        if category:
           
            workspace_id = category.workspace.workspace_id
            # Verify the user has permission to be creating fields (only admins)
            user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
            if user_workspace['workspace']:
                workspace = user_workspace['workspace']
            
                query = request.query_params.get('keyword')
                if query == None:
                    query = ''

                fields = Field.objects.filter(
                    category=category,
                    name__icontains=query,
                    status='active',
                ).order_by('name')

                page = request.query_params.get('page')
                paginator = Paginator(fields, 5)

                try:
                    fields = paginator.page(page)
                except PageNotAnInteger:
                    fields = paginator.page(1)
                except EmptyPage:
                    fields = paginator.page(paginator.num_pages)

                if page == None:
                    page = 1

                page = int(page)
                print('Page:', page)
                serializer = FieldSerializer(fields, many=True)
                return Response({'fields': serializer.data, 'page': page, 'pages': paginator.num_pages})
                    
            else:
                message = {'detail': user_workspace['message']}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)

        else:
            message = {'detail': 'Category does not exist'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Field category_id is missing from the request'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getField(request, field_id):

    user = request.user

    # Check if the field is valid
    field = Field.objects.filter(field_id=field_id, status='active').first()
    if field:

        category = field.category
        workspace = category.workspace
        workspace_id = workspace.workspace_id
        # Verify the user has permission for the field's workspace
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['user', 'admin'])
        if user_workspace['workspace']:
            
            serializer = FieldSerializer(field, many=False)
            return Response({'fields': serializer.data})
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Field does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateField(request, field_id):
    data = request.data
    user = request.user

    # Check if the field is valid
    field = Field.objects.filter(field_id=field_id, status='active').first()
    if field:
        category = field.category
        workspace = category.workspace
        workspace_id = workspace.workspace_id
        # Verify the user has permission for the field's workspace and can edit
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            
            field.name = data['name']
            field.save()
            serializer = FieldSerializer(field, many=False)
            return Response({'fields': serializer.data})
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Field does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def archiveField(request, field_id):
    
    user = request.user

    # Check if the field is valid
    field = Field.objects.filter(field_id=field_id, status='active').first()
    if field:
        category = field.category
        workspace = category.workspace
        workspace_id = workspace.workspace_id
        # Verify the user has permission for the field's workspace and can edit
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            field.status = 'archived'
            field.save()
            message = {'detail': 'Field was archived'}
            return Response(message, status=200)
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Field does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
