from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.template.loader import render_to_string
from rest_framework.decorators import api_view

import json
import boto3

from core import settings
from core.utils import *
from files.tasks import *

import logging

logger = logging.getLogger("Django Starter Project")

from drf_spectacular.utils import extend_schema


@login_required(login_url="login")
@require_http_methods(["POST"])
@extend_schema(exclude=True)
def fetch_file_sign(request):
    
    if is_ajax(request):

        if request.method == "POST":

            data = json.loads(request.body)
            files_to_sign = None
            if "filesToSign" in data:
                files_to_sign = data["filesToSign"]
            if not files_to_sign:
                return JsonResponse(
                    {"error": "Missing the 'files_to_sign' parameter."}, status=400
                )

            files_to_save = []

            for file_to_sign in files_to_sign:
                file_id = file_to_sign["id"]
                original_name = file_to_sign["file_name"]
                file_type = file_to_sign["file_type"]
                file_extension = file_to_sign["file_extension"]
                file_size = file_to_sign["file_size"]
                file_size_mb = file_to_sign["file_size_mb"]
                file_name = "private/uploads/" + randomlongstr() + "." + file_extension
                valid = file_to_sign["valid"]
                template = None
                if valid:
                    S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME

                    s3 = boto3.client(
                        "s3",
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                        region_name=settings.AWS_S3_REGION,
                    )

                    presigned_post = s3.generate_presigned_post(
                        Bucket=S3_BUCKET,
                        Key=file_name,
                        Fields={"acl": "private", "Content-Type": file_type},
                        Conditions=[{"acl": "private"}, {"Content-Type": file_type}],
                        ExpiresIn=600,
                    )

                    file_to_sign["presigned"] = presigned_post
                    file_to_sign["url"] = "https://%s.s3.amazonaws.com/%s" % (
                        S3_BUCKET,
                        file_name,
                    )

                    template = "app/files/file-upload-placeholder.html"
                else:
                    template = "app/files/file-upload-placeholder-invalid.html"

                html = render_to_string(
                    template_name=template,
                    context={
                        "id": file_id,
                        "name": file_name,
                        "original_name": original_name,
                        "type": file_type,
                        "size": file_size,
                        "size_mb": file_size_mb,
                    },
                )

                file_to_sign["placeholder"] = html
                file_to_sign["file_original_name"] = original_name

                files_to_save.append(file_to_sign)

            response_object = {"files": files_to_save}
            response = JsonResponse(response_object)
            response.status_code = 200
            return response
