from accounts.models import *
from core.utils import *
from backend.models import *
from backend.utils import *
import pytz

import boto3
from django.conf import settings
from files.models import *
from files.tasks import *

import urllib.parse

from decimal import Decimal, InvalidOperation

from rest_framework import permissions

import datetime

import logging

logger = logging.getLogger("Django Starter Project")



class IsAuthenticatedOrHasAPIKey(permissions.BasePermission):
    """
    Allows access to authenticated users or users with a valid API key.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated via JWT
        if request.user and request.user.is_authenticated:
            return True

        # Check for API Key in the Authorization header
        """
        key_request = request.META.get("HTTP_AUTHORIZATION")
        if key_request:
            try:
                key = key_request.split()[1]
                api_key = InvestigationAPIKey.objects.get_from_key(key)
                if api_key:
                    # Attach the user associated with the API key to the request
                    request.user = api_key.user
                    return True
            except InvestigationAPIKey.DoesNotExist:
                pass  # API Key is not valid
        """

        # Neither JWT nor API Key is valid
        return False


def check_params(data, params):
    valid = True
    errors = []

    # Mapping of type strings to actual Python types
    type_mapping = {
        "string": str,
        "integer": int,
        "float": (float, int),
        "decimal": Decimal,
        "object_list": list,
        "string_list": list,
        "boolean": bool,
        "object": dict,
        "date": dict,
        "datetime": dict,
    }

    # Function to validate individual parameter
    def validate_param(param_name, param_object, param_value):
        nonlocal errors

        expected_type = type_mapping[param_object["type"]]

        valid = True

        # Type validation
        if param_object["type"] == "decimal":
            try:
                decimal_value = Decimal(str(param_value))
                data[param_name] = decimal_value
            except InvalidOperation:
                errors.append(f'Parameter: {param_name} is not a valid decimal')
                valid = False
        
        else:
            if not isinstance(param_value, expected_type):
                errors.append(
                    f'Parameter: {param_name} is not of type {param_object["type"]}'
                )
                valid = False

        # Additional validations based on type
        if param_object["type"] == "string":
            if param_value.strip() == "":
                errors.append(f"Empty parameter: {param_name}")
                valid = False
            
            if param_object["param"] == "group_id" and app is not None:
                valid = validate_object_exists(param_name, "group", param_value, app, errors)
            
            if param_object["param"] == "farmer_id" and app is not None:
                valid = validate_object_exists(param_name, "farmer", param_value, app, errors)


            if "length" in param_object and len(param_value) > param_object["length"]:
                errors.append(
                    f'Parameter: {param_name} exceeds allowed length of {param_object["length"]}'
                )
                valid = False

            if "options" in param_object and param_value not in param_object["options"]:
                errors.append(
                    f'Parameter: {param_name} does not have a valid option from values {param_object["options"]}'
                )
                valid = False

        if param_object["type"] == "boolean":
            if not isinstance(param_value, bool):
                errors.append(f'Parameter: {param_name} is not a boolean')
                valid = False

        if param_object["type"] == "integer":
            if not isinstance(param_value, int):
                errors.append(f'Parameter: {param_name} is not an integer')
                valid = False

        if param_object["type"] == "float":
            if not isinstance(param_value, (float, int)):  # Allow int for float type
                errors.append(f'Parameter: {param_name} is not a float')
                valid = False

        if param_object["type"] == "object":
            if not isinstance(param_value, dict):
                errors.append(f'Parameter: {param_name} is not a valid JSON object')
                valid = False
            
        if (param_object["type"] == "object_list" or param_object["type"] == "string_list"):
            if len(param_value) == 0:
                errors.append(f"Parameter {param_name} cannot be an empty list")
                valid = False

        if param_object["type"] == "date":
            try:
                datetime.datetime(
                    param_value["year"], param_value["month"], param_value["day"]
                )
            except (ValueError, KeyError):
                errors.append(
                    f"Parameter: {param_name} - included year, month, and day is not a valid date"
                )
                valid = False

        if param_object["type"] == "datetime":
            try:
                datetime.datetime(
                    param_value["year"],
                    param_value["month"],
                    param_value["day"],
                    param_value["hour"],
                    param_value["minute"],
                    param_value["second"],
                )
            except (ValueError, KeyError):
                errors.append(
                    f"Parameter: {param_name} - included year, month, day, hours, minutes, and second is not a valid date"
                )
                valid = False

        return valid

    # Iterate over each expected parameter
    for param_object in params:
        param_name = param_object["param"]

        # Check if the parameter is enabled
        if not param_object.get("enabled", True):
            if param_name in data:
                errors.append(f"Parameter {param_name} is not enabled for this operation")
                valid = False
    
        # Required parameter check
        if param_object["required"] and param_name not in data:
            errors.append(f"Missing parameter: {param_name}")
            valid = False

        # Validate the parameter if it exists and is not None
        if param_name in data:
            param_value = data[param_name]
            if param_value is not None:
                if not validate_param(param_name, param_object, param_value):
                    valid = False

    # Check for unrecognized parameters
    recognized_params = {param["param"] for param in params}
    unrecognized_params = set(data.keys()) - recognized_params
    for param in unrecognized_params:
        errors.append(f"Parameter not valid: {param}")
        valid = False

    return {"valid": valid, "errors": errors}

def validate_object_exists(param_name, object_type, param_value, app, errors):
    if param_value is None:
        errors.append(f'Parameter: {param_name} is missing {object_type}_id')
        return False

    if object_type == "group":
        obj = Group.objects.filter(app=app, group_id=param_value).first()
        if not obj or obj.status != "active":
            errors.append(f'Parameter: {param_name} is not a valid {object_type} object')
            return False
    
    elif object_type == "farmer":
        obj = Farmer.objects.filter(app=app, farmer_id=param_value).first()
        if not obj or obj.status != "active":
            errors.append(f'Parameter: {param_name} is not a valid {object_type} object')
            return False

    return True


def create_file_object_from_upload_data(file_data, user):
    """
    Create a File object from the provided upload data.
    Returns the created File instance without associating it to anything.
    """
    S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME
    root_url = f"https://{S3_BUCKET}.s3.amazonaws.com/private/"

    original_name = file_data["original_name"]
    file_type = file_data["file_type"]
    file_extension = file_data["file_name"].split('.')[-1]
    file_size = file_data["file_size"]
    file_size_mb = file_data["file_size_mb"]
    file_name = file_data["file_name"]
    url = file_data["url"]
    save_url = url.replace(root_url, "")

    file_display_type = get_file_display_type(file_type)

    media_file = File(
        file=save_url,
        display_id=randomstr(),
        file_name=file_name,
        original_name=original_name,
        display_name=original_name,
        file_type=file_type,
        file_size=file_size,
        file_size_mb=file_size_mb,
        file_display_type=file_display_type,
        file_extension=f".{file_extension}",
        user=user
    )
    
    media_file.save()

    # Background processing for thumbnails if the file is an image
    # process_thumbnails.delay(media_file.id)

    return media_file


def parse_date(date_dict):
    if date_dict:
        return datetime.datetime(
            year=date_dict['year'],
            month=date_dict['month'],
            day=date_dict['day'],
            hour=date_dict['hour'],
            minute=date_dict['minute'],
            second=date_dict['second'],
            tzinfo=pytz.timezone(date_dict['timezone'])
        )
    return None
