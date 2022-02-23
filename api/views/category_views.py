from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from documents.models import Category
from api.serializers import CategorySerializer

from rest_framework import status

from .permissions_check import *
from core.utils import randomstr


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createCategory(request):
    user = request.user
    data = request.data

    if 'workspace_id' in data:
        workspace_id = data['workspace_id']
        # Verify the user has permission to be creating categories (only admins)
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            workspace = user_workspace['workspace']
            # Create the category
            try:

                category = Category.objects.create(
                    name=data['name'],
                    workspace=workspace,
                    category_id = randomstr(),
                    created_user=user,
                )

                serializer = CategorySerializer(category, many=False)
                return Response(serializer.data)
    
            except Exception as e:
                print(e)
                message = {'detail': 'There was an error creating this category'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Field workspace_id is missing from the request'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCategories(request):
    user = request.user
    data = request.data

    if 'workspace_id' in data:
        workspace_id = data['workspace_id']
        # Verify the user has permission to be creating categories (only admins)
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            workspace = user_workspace['workspace']
            
            query = request.query_params.get('keyword')
            if query == None:
                query = ''

            categories = Category.objects.filter(
                workspace=workspace,
                name__icontains=query,
                status='active',
            ).order_by('name')

            page = request.query_params.get('page')
            paginator = Paginator(categories, 5)

            try:
                categories = paginator.page(page)
            except PageNotAnInteger:
                categories = paginator.page(1)
            except EmptyPage:
                categories = paginator.page(paginator.num_pages)

            if page == None:
                page = 1

            page = int(page)
            print('Page:', page)
            serializer = CategorySerializer(categories, many=True)
            return Response({'categories': serializer.data, 'page': page, 'pages': paginator.num_pages})
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Field workspace_id is missing from the request'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCategory(request, category_id):

    user = request.user

    # Check if the category is valid
    category = Category.objects.filter(category_id=category_id, status='active').first()
    if category:
        workspace_id = category.workspace.workspace_id
        # Verify the user has permission for the category's workspace
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['user', 'admin'])
        if user_workspace['workspace']:
            
            serializer = CategorySerializer(category, many=False)
            return Response({'categories': serializer.data})
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Category does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateCategory(request, category_id):
    data = request.data
    user = request.user

    # Check if the category is valid
    category = Category.objects.filter(category_id=category_id, status='active').first()
    if category:
        workspace_id = category.workspace.workspace_id
        # Verify the user has permission for the category's workspace and can edit
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            
            category.name = data['name']
            category.save()
            serializer = CategorySerializer(category, many=False)
            return Response({'categories': serializer.data})
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Category does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def archiveCategory(request, category_id):
    
    user = request.user

    # Check if the category is valid
    category = Category.objects.filter(category_id=category_id, status='active').first()
    if category:
        workspace_id = category.workspace.workspace_id
        # Verify the user has permission for the category's workspace and can edit
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            category.status = 'archived'
            category.save()
            message = {'detail': 'Category was archived'}
            return Response(message, status=200)
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Category does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
