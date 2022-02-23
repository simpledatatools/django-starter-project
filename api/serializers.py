from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import *
from documents.models import *

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'name', 'isAdmin']

    def get_id(self, obj):
        return obj.id

    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email

        return name

class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'name', 'isAdmin', 'token']
    
    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

    def get_id(self, obj):
        return obj.id

class WorkspaceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Workspace
        fields = ['workspace_id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    workspace_id = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['category_id', 'workspace_id', 'name']

    def get_workspace_id(self, obj):
        return obj.workspace.workspace_id

class FieldSerializer(serializers.ModelSerializer):
    category_id = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Field
        fields = ['field_id', 'category_id', 'name', 'type', 'config']

    def get_category_id(self, obj):
        return obj.category.category_id

class TagSerializer(serializers.ModelSerializer):
    workspace_id = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Tag
        fields = ['tag_id', 'workspace_id', 'label']

    def get_workspace_id(self, obj):
        return obj.workspace.workspace_id

class DocumentSerializer(serializers.ModelSerializer):
    category_id = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Document
        fields = ['document_id', 'category_id', 'config']

    def get_category_id(self, obj):
        return obj.category.category_id