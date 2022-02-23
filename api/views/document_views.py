from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from documents.models import Document
from api.serializers import DocumentSerializer

from rest_framework import status

from .permissions_check import *
from core.utils import randomstr


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createDocument(request):
    user = request.user
    data = request.data

    if 'category_id' in data:
        category_id = data['category_id']

        category = Category.objects.filter(category_id=category_id, status='active').first()
        if category:
           
            workspace_id = category.workspace.workspace_id
            # Verify the user has permission to be creating documents (only admins)
            user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
            if user_workspace['workspace']:
                workspace = user_workspace['workspace']
                # Create the document
                try:

                    document = Document.objects.create(
                        category=category,
                        document_id = randomstr(),
                        created_user=user,
                    )
                    
                    if 'config' in data:
                        document.config=data['config']
                        document.save()

                    serializer = DocumentSerializer(document, many=False)
                    return Response(serializer.data)
        
                except Exception as e:
                    print(e)
                    message = {'detail': 'There was an error creating this document'}
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                message = {'detail': user_workspace['message']}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)

        else:
            message = {'detail': 'Category does not exist'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Document category_id is missing from the request'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getDocuments(request):
    user = request.user
    data = request.data

    if 'category_id' in data:
        category_id = data['category_id']

        category = Category.objects.filter(category_id=category_id, status='active').first()
        if category:
           
            workspace_id = category.workspace.workspace_id
            # Verify the user has permission to be creating documents (only admins)
            user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
            if user_workspace['workspace']:
                workspace = user_workspace['workspace']
            
                query = request.query_params.get('keyword')
                if query == None:
                    query = ''

                # TODO eventually query by block content

                documents = Document.objects.filter(
                    category=category,
                    status='active',
                )

                page = request.query_params.get('page')
                paginator = Paginator(documents, 5)

                try:
                    documents = paginator.page(page)
                except PageNotAnInteger:
                    documents = paginator.page(1)
                except EmptyPage:
                    documents = paginator.page(paginator.num_pages)

                if page == None:
                    page = 1

                page = int(page)
                print('Page:', page)
                serializer = DocumentSerializer(documents, many=True)
                return Response({'documents': serializer.data, 'page': page, 'pages': paginator.num_pages})
                    
            else:
                message = {'detail': user_workspace['message']}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)

        else:
            message = {'detail': 'Category does not exist'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Document category_id is missing from the request'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getDocument(request, document_id):

    user = request.user

    # Check if the document is valid
    document = Document.objects.filter(document_id=document_id, status='active').first()
    if document:

        category = document.category
        workspace = category.workspace
        workspace_id = workspace.workspace_id
        # Verify the user has permission for the document's workspace
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['user', 'admin'])
        if user_workspace['workspace']:
            
            serializer = DocumentSerializer(document, many=False)
            return Response({'documents': serializer.data})
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Document does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateDocument(request, document_id):
    data = request.data
    user = request.user

    # Check if the document is valid
    document = Document.objects.filter(document_id=document_id, status='active').first()
    if document:
        category = document.category
        workspace = category.workspace
        workspace_id = workspace.workspace_id
        # Verify the user has permission for the document's workspace and can edit
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            
            # TODO nothing to update at this time
            
            serializer = DocumentSerializer(document, many=False)
            return Response({'documents': serializer.data})
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Document does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def archiveDocument(request, document_id):
    
    user = request.user

    # Check if the document is valid
    document = Document.objects.filter(document_id=document_id, status='active').first()
    if document:
        category = document.category
        workspace = category.workspace
        workspace_id = workspace.workspace_id
        # Verify the user has permission for the document's workspace and can edit
        user_workspace = check_workspace_permissions(user=user, workspace_id=workspace_id, roles=['admin'])
        if user_workspace['workspace']:
            document.status = 'archived'
            document.save()
            message = {'detail': 'Document was archived'}
            return Response(message, status=200)
            
        else:
            message = {'detail': user_workspace['message']}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    else:
        message = {'detail': 'Document does not exist'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
