from rest_framework import serializers
from .models import File

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            'id', 'legacy_id', 'display_id', 'file', 'thumbnail', 'micro_thumbnail', 
            'created_at', 'user', 'file_name', 'original_name', 'display_name', 
            'file_size', 'file_size_mb', 'file_type', 'file_extension', 
            'file_display_type', 'data', 'status'
        ]
        read_only_fields = ['id', 'display_id', 'created_at']
