from drf_spectacular.utils import OpenApiResponse, OpenApiTypes, inline_serializer
from rest_framework import serializers

# Error response schema
error_response = OpenApiResponse(
    response=inline_serializer(
        name='ErrorResponseSerializer',
        fields={
            "errors": serializers.ListSerializer(
                child=serializers.CharField(),
                help_text="List of error messages"
            )
        }
    ),
    description="Bad request",
    examples={
        "application/json": {
            "errors": ["Error message 1", "Error message 2"]
        }
    }
)