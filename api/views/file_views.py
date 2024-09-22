from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import boto3
from django.conf import settings
from core.utils import randomlongstr
from rest_framework import status
from drf_spectacular.utils import extend_schema

import logging

logger = logging.getLogger("Django Starter Project")


@extend_schema(exclude=True)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_file_sign(request):
    data = request.data
    files_to_sign = data.get("filesToSign")
    
    if not files_to_sign:
        return Response(
            {"success": False, "message": "Missing the 'files_to_sign' param"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    signed_files = []

    for file_to_sign in files_to_sign:
        original_name = file_to_sign["file_name"]
        file_type = file_to_sign["file_type"]
        file_extension = file_to_sign["file_extension"]
        file_size = file_to_sign.get("file_size", None)
        file_size_mb = file_to_sign.get("file_size_mb", None)
        file_name = f"private/uploads/{randomlongstr()}.{file_extension}"

        signed_file = {
            "original_name": original_name,
            "file_name": file_name,
            "file_type": file_type,
            "file_size": file_size,
            "file_size_mb": file_size_mb,
            "file_extension": file_extension
        }
        
        S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME

        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION,
        )

        try:
            presigned_post = s3.generate_presigned_post(
                Bucket=S3_BUCKET,
                Key=file_name,
                Fields={"acl": "private", "Content-Type": file_type},
                Conditions=[{"acl": "private"}, {"Content-Type": file_type}],
                ExpiresIn=600,
            )

            signed_file["presigned"] = presigned_post
            signed_file["url"] = f"https://{S3_BUCKET}.s3.amazonaws.com/{file_name}"
        
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            continue

        signed_files.append(signed_file)

    return Response({"success": True, "files": signed_files}, status=status.HTTP_200_OK)
