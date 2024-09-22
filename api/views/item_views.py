from django.shortcuts import render
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from core.utils import *

from rest_framework import status
from django.db.models import Q

from core.utils import randomstr

from api.views.utils import *

from backend.models import *

import json
from django.utils import timezone
import datetime

import logging

logger = logging.getLogger("Django Starter Project")

# Custom decorators
from backend.decorators import *

# Serializers
from api.serializers.item_serializers import *

from api.views.utils import *

# API documentation
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from api.documentation.item_documentation import *
from api.documentation.common_elements import *

# Auth
from api.views.utils import IsAuthenticatedOrHasAPIKey

from functools import lru_cache

# -----------------------------------------------------------------------------------------------------------------------------
# Utils to fetch app settings
# -----------------------------------------------------------------------------------------------------------------------------

# Base field configurations
BASE_FIELDS = {
    "item_id": {"param": "item_id", "type": "string", "required": False, "length": 32},
    "name": {"param": "name", "type": "string", "required": True},
    "cover_photo": {"param": "cover_photo", "type": "object", "required": False},
}

# Specific configurations
SEARCH_FIELDS = {'name', 'description', 'address', 'phone_number'}
RETURN_FIELDS = set(BASE_FIELDS.keys())
RETURN_FIELDS.update(["created_at", "created_user", "last_updated"])
SORT_FIELDS = {
    "name_asc": "name",
    "name_desc": "-name",
}

ADD_FIELDS = [
    BASE_FIELDS["item_id"],
    BASE_FIELDS["name"],
    BASE_FIELDS["cover_photo"],
]

UPDATE_FIELDS = [
    BASE_FIELDS["name"],
    BASE_FIELDS["cover_photo"],
]

BULK_UPDATE_FIELDS = [
    {**BASE_FIELDS["item_id"], "required": True},
    BASE_FIELDS["name"],
    BASE_FIELDS["cover_photo"],
]

SPECTACULAR_TAG_NAME = "Items"

DEFAULT_PAGE_SIZE = 25


# -----------------------------------------------------------------------------------------------------------------------------
# Getting items
# -----------------------------------------------------------------------------------------------------------------------------

@extend_schema(
    tags=[SPECTACULAR_TAG_NAME],
    operation_id="Get Item List",
    description="Retrieve a list of items",
    responses={
        200: OpenApiResponse(response=item_list_response_schema, description="Item list retrieved successfully"),
        400: OpenApiResponse(response=error_response, description="Bad request"),
        403: OpenApiResponse(response=error_response, description="Forbidden"),
    },
    parameters=[
        OpenApiParameter(
            name="search",
            description="Search term",
            type=str,
        ),
        OpenApiParameter(
            name="search_fields",
            description="Comma-separated list of fields to search",
            type=str,
            required=False,
        ),
        OpenApiParameter(
            name="sort",
            description="Sort option",
            type=str,
        ),
        OpenApiParameter(
            name="page",
            description="Page number",
            type=int,
        ),
        OpenApiParameter(
            name="page_size",
            description="Number of items per page",
            type=int,
        ),
        OpenApiParameter(
            name="start_date",
            description="Start date (YYYY-MM-DD)",
            type=str,
            required=False,
        ),
        OpenApiParameter(
            name="end_date",
            description="End date (YYYY-MM-DD)",
            type=str,
            required=False,
        ),
        OpenApiParameter(
            name="return_fields",
            description="Comma-separated list of fields to return",
            type=str,
            required=False,
        ),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def get_items(request):
    user = request.user

    # Extract start_date and end_date from query parameters
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    # Filter items based on user, status, and timestamp range
    query = (
        Item.objects.select_related("created_user")
        .filter(status="active")
        .order_by("-created_at")
    )
    
    # Apply date filtering if start_date and end_date are provided
    if start_date and end_date:
        try:
            start_datetime = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_datetime = datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
            query = query.filter(created_at__range=(start_datetime, end_datetime))
        except ValueError:
            return Response(
                {"errors": ["Invalid date format. Use YYYY-MM-DD."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Search filtering if applicable
    search_query = request.query_params.get("search", "").strip()
    search_fields = request.query_params.get("search_fields", "").split(",")
    search_fields = [field for field in search_fields if field in SEARCH_FIELDS]
    if search_query:
        search_conditions = Q()
        fields_to_search = search_fields if search_fields else SEARCH_FIELDS
        for field in fields_to_search:
            search_conditions |= Q(**{f"{field}__icontains": search_query})
        query = query.filter(search_conditions)

    # Sorting
    sort_option = request.query_params.get("sort", "").strip()
    query = query.order_by(
        SORT_FIELDS.get(sort_option, "-created_at")
    )

    # Pagination
    try:
        page_number = int(request.query_params.get("page", 1))
    except ValueError:
        return Response(
            {"errors": ["Page number must be an integer."]},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        page_size = int(request.query_params.get("page_size", DEFAULT_PAGE_SIZE))
        if page_size > 100:
            return Response(
                {"errors": ["Page size cannot exceed 100."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except ValueError:
        return Response(
            {"errors": ["Page size must be an integer."]},
            status=status.HTTP_400_BAD_REQUEST,
        )
    paginator = Paginator(query, page_size)

    try:
        items_page = paginator.page(page_number)
    except PageNotAnInteger:
        items_page = paginator.page(1)
    except EmptyPage:
        items_page = paginator.page(paginator.num_pages)

    serializer = ItemSerializer(items_page, many=True)

    # Process return_fields parameter
    return_fields = request.query_params.get("return_fields", "").split(",")
    return_fields = [field for field in return_fields if field in RETURN_FIELDS]
    if return_fields:
        data = [{field: app.get(field, None) for field in return_fields} for app in serializer.data]
    else:
        data = serializer.data
    
    response_data = {
        "items": data,
        "page": items_page.number,
        "pages": paginator.num_pages,
        "records_count": paginator.count,
    }

    return Response(response_data)


@extend_schema(
    tags=[SPECTACULAR_TAG_NAME],
    operation_id="Get Item",
    description="Retrieve a Item",
    responses={
        200: OpenApiResponse(response=item_response_schema, description="Item retrieved successfully"),
        400: OpenApiResponse(response=error_response, description="Bad request"),
        403: OpenApiResponse(response=error_response, description="Forbidden"),
    },
    parameters=[
        OpenApiParameter(
            name="return_fields",
            description="Comma-separated list of fields to return",
            type=str,
            required=False,
        ),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def get_item(request, item_id):
    user = request.user

    item = (
        Item.objects.select_related("created_user")
        .filter(item_id=item_id, status="active")
        .first()
    )
    if item:
        serializer = ItemSerializer(item, many=False)

        # Process return_fields parameter
        return_fields = request.query_params.get("return_fields", "").split(",")
        return_fields = [field for field in return_fields if field in RETURN_FIELDS]
        if return_fields:
            data = {field: serializer.data.get(field, None) for field in return_fields}
        else:
            data = serializer.data

        return Response(data)
    else:
        return Response(
            {"errors": ["Item does not exist."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

@extend_schema(
    tags=[SPECTACULAR_TAG_NAME],
    operation_id="Get Count of Items",
    description="Retrieve the number of Items, optionally filtered by date range",
    responses={
        200: OpenApiResponse(response=item_count_response_schema, description="Count of items retrieved successfully"),
        400: OpenApiResponse(response=error_response, description="Bad request"),
        403: OpenApiResponse(response=error_response, description="Forbidden"),
    },
    parameters=[
        OpenApiParameter(
            name="start_date",
            description="Start date (YYYY-MM-DD)",
            type=str,
            required=False,
        ),
        OpenApiParameter(
            name="end_date",
            description="End date (YYYY-MM-DD)",
            type=str,
            required=False,
        ),
    ],
)
@api_view(["GET"])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def get_item_count(request):
    user = request.user

    query = Item.objects.filter(status="active")

    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    if start_date and end_date:
        try:
            start_datetime = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_datetime = datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
            query = query.filter(created_at__range=(start_datetime, end_datetime))
        except ValueError:
            return Response(
                {"errors": ["Invalid date format. Use YYYY-MM-DD."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

    count = query.count()
    return Response({"count": count})


# -----------------------------------------------------------------------------------------------------------------------------
# Adding items
# -----------------------------------------------------------------------------------------------------------------------------

@extend_schema(
    tags=[SPECTACULAR_TAG_NAME],
    operation_id="Add Item",
    description="Add a Item",
    request={
        "application/json": item_add_schema,
    },
    responses={
        201: OpenApiResponse(response=item_response_schema, description="Item created successfully"),
        400: OpenApiResponse(response=error_response, description="Bad request"),
        403: OpenApiResponse(response=error_response, description="Forbidden"),
        409: OpenApiResponse(response=error_response, description="Conflict"),
        500: OpenApiResponse(response=error_response, description="Internal server error"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def add_item(request):
    user = request.user

    item_object = request.data

    valid_params = check_params(
        item_object,
        ADD_FIELDS,
    )

    if valid_params["valid"]:
        item_id = item_object.get("item_id")
        if item_id and Item.objects.filter(item_id=item_id).exists():
            return Response(
                {"errors": ["Item ID already exists."]},
                status=status.HTTP_409_CONFLICT
            )
        try:
            with transaction.atomic():
                result = create_item_record(item_object, request.user)
            serializer = ItemSerializer(result["item"])
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error creating Item: {e}")
            return Response(
                {"errors": ["Failed to create Item."]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    else:
        return Response(
            {"errors": valid_params["errors"]}, status=status.HTTP_400_BAD_REQUEST
        )

@extend_schema(
    tags=[SPECTACULAR_TAG_NAME],
    operation_id="Add Items",
    description="Add a list of Items",
    request={
        "application/json": item_add_request_body,
    },
    responses={
        200: OpenApiResponse(response=add_items_response_schema, description="Items added successfully"),
        400: OpenApiResponse(response=error_response, description="Bad request"),
        403: OpenApiResponse(response=error_response, description="Forbidden"),
        500: OpenApiResponse(response=error_response, description="Internal server error"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def add_items(request):
    user = request.user

    data = request.data

    items_data = data.get("items")
    if not isinstance(items_data, list) or not items_data:
        return Response(
            {"errors": ["Items list is required and should not be empty."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    response_data = {"items_added": [], "items_not_added": []}

    try:
        with transaction.atomic():
            for index, item_object in enumerate(items_data):

                valid_params = check_params(
                    item_object,
                    ADD_FIELDS,
                )

                if valid_params["valid"]:
                    item_id = item_object.get("item_id")
                    if item_id and Item.objects.filter(item_id=item_id).exists():
                        response_data["items_not_added"].append(
                            {
                                "index": index,
                                "submitted_object": item_object,
                                "errors": ["Item ID already exists."],
                            }
                        )
                    else:
                        result = create_item_record(
                            item_object, request.user
                        )
                        serializer = ItemSerializer(result["item"])
                        response_data["items_added"].append(serializer.data)
                else:
                    response_data["items_not_added"].append(
                        {
                            "index": index,
                            "submitted_object": item_object,
                            "errors": valid_params["errors"],
                        }
                    )
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error adding items: {e}")
        return Response(
            {"errors": ["Failed to add items."]},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# -----------------------------------------------------------------------------------------------------------------------------
# Updating items
# -----------------------------------------------------------------------------------------------------------------------------


@extend_schema(
    tags=[SPECTACULAR_TAG_NAME],
    operation_id="Update Item",
    description="Update a Item",
    request={
        "application/json": single_item_update_schema,
    },
    responses={
        201: OpenApiResponse(response=item_response_schema, description="Item updated successfully"),
        400: OpenApiResponse(response=error_response, description="Bad request"),
        403: OpenApiResponse(response=error_response, description="Forbidden"),
        500: OpenApiResponse(response=error_response, description="Internal server error"),
    },
)
@api_view(["PUT"])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def update_item(request, item_id):
    item_object = request.data
    user = request.user

    valid_params = check_params(
        item_object,
        UPDATE_FIELDS,
    )

    if valid_params["valid"]:
        try:
            with transaction.atomic():
                item = Item.objects.filter(
                    item_id=item_id, status="active"
                ).first()
                if item:
                    result = update_item_record(
                        item, item_object, user
                    )
                    serializer = ItemSerializer(result["item"])
                    return Response(
                        serializer.data, status=status.HTTP_200_OK
                    )
                else:
                    logger.error(
                        f"Error updating item: item does not exist."
                    )
                    return Response(
                        {"errors": ["item does not exist."]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        except Exception as e:
            logger.error(f"Error updating item: {e}")
            return Response(
                {"errors": ["Failed to update item."]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    else:
        return Response(
            {"errors": valid_params["errors"]}, status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    tags=[SPECTACULAR_TAG_NAME],
    operation_id="Update Items",
    description="Update a list of items",
    request={
        "application/json": bulk_item_update_schema,
    },
    responses={
        200: OpenApiResponse(response=update_items_response_schema, description="Items updated successfully"),
        400: OpenApiResponse(response=error_response, description="Bad request"),
        403: OpenApiResponse(response=error_response, description="Forbidden"),
        500: OpenApiResponse(response=error_response, description="Internal server error"),
    },
)
@api_view(["PUT"])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def update_items(request):
    data = request.data
    user = request.user

    items_data = data.get("items")
    if not isinstance(items_data, list) or not items_data:
        return Response(
            {"errors": ["Items list is required and should not be empty."]},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if len(items_data) > 100:  # Check if there are more than 100 objects
        return Response(
            {"errors": ["Cannot perform bulk operations on more than 100 objects."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    response_data = {"items_updated": [], "items_not_updated": []}

    try:
        with transaction.atomic():
            for index, item_object in enumerate(items_data):
                valid_params = check_params(
                    item_object,
                    BULK_UPDATE_FIELDS,
                )

                if valid_params["valid"]:
                    item_id = item_object["item_id"]
                    item = Item.objects.filter(
                        item_id=item_id, status="active"
                    ).first()
                    if item:
                        try:
                            result = update_item_record(
                                item, item_object, user
                            )
                            serializer = ItemSerializer(result["item"])
                            response_data["items_updated"].append(
                                serializer.data
                            )
                        except Item.DoesNotExist:
                            response_data["items_not_updated"].append(
                                {
                                    "index": index,
                                    "submitted_object": item_object,
                                    "errors": ["Item could not be updated"],
                                }
                            )
                    else:
                        response_data["items_not_updated"].append(
                            {
                                "index": index,
                                "submitted_object": item_object,
                                "errors": ["Item not found"],
                            }
                        )
                else:
                    response_data["items_not_updated"].append(
                        {
                            "index": index,
                            "submitted_object": item_object,
                            "errors": valid_params["errors"],
                        }
                    )

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error updating items: {e}")
        return Response(
            {"errors": ["Failed to update items."]},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# -----------------------------------------------------------------------------------------------------------------------------
# Archiving items
# -----------------------------------------------------------------------------------------------------------------------------

@extend_schema(
    tags=[SPECTACULAR_TAG_NAME],
    operation_id="Archive Item",
    description="Archive a item",
    responses={
        200: OpenApiResponse(response=archive_item_schema, description="Item archived successfully"),
        400: OpenApiResponse(response=error_response, description="Bad request"),
        403: OpenApiResponse(response=error_response, description="Forbidden"),
        500: OpenApiResponse(response=error_response, description="Internal server error"),
    },
)
@api_view(["PUT"])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def archive_item(request, item_id):
    user = request.user

    item = (
        Item.objects.select_related("created_user")
        .filter(item_id=item_id, status="active")
        .first()
    )
    if item:
        try:
            with transaction.atomic():
                item.status = "archived"
                item.save()
            serializer = ItemSerializer(item)
            return Response(
                {"item_id": item_id}, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error archiving item: {e}")
            return Response(
                {"errors": ["Failed to archive item."]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    else:
        return Response(
            {"errors": ["Item does not exist."]},
            status=status.HTTP_400_BAD_REQUEST,
        )


@extend_schema(
    tags=[SPECTACULAR_TAG_NAME],
    operation_id="Archive Items",
    description="Archive a list of items",
    request={
        "application/json": item_archive_request_body,
    },
    responses={
        200: OpenApiResponse(response=archive_items_response_schema, description="Items archived successfully"),
        400: OpenApiResponse(response=error_response, description="Bad request"),
        403: OpenApiResponse(response=error_response, description="Forbidden"),
        500: OpenApiResponse(response=error_response, description="Internal server error"),
    },
)
@api_view(["PUT"])
@permission_classes([IsAuthenticatedOrHasAPIKey])
def archive_items(request):
    data = request.data
    user = request.user

    items_data = data.get("items")
    if not isinstance(items_data, list) or not items_data:
        return Response(
            {"errors": ["Items list is required and should not be empty."]},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if len(items_data) > 100:  # Check if there are more than 100 objects
        return Response(
            {"errors": ["Cannot perform bulk operations on more than 100 objects."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    response_data = {"items_archived": [], "items_not_archived": []}

    try:
        with transaction.atomic():
            for index, item_object in enumerate(items_data):
                valid_params = check_params(
                    item_object,
                    [
                        {
                            "param": "item_id",
                            "type": "string",
                            "required": True,
                            "length": 32,
                        },
                    ],
                )

                if valid_params["valid"]:
                    item_id = item_object["item_id"]
                    try:
                        item = Item.objects.get(
                            item_id=item_id, status="active"
                        )
                        item.status = "archived"
                        item.save()
                        serializer = ItemSerializer(item)
                        response_data["items_archived"].append({"item_id": serializer.data["item_id"]})
                    except Item.DoesNotExist:
                        response_data["items_not_archived"].append(
                            {
                                "index": index,
                                "submitted_object": item_object,
                                "errors": ["Item not found"],
                            }
                        )
                else:
                    response_data["items_not_archived"].append(
                        {
                            "index": index,
                            "submitted_object": item_object,
                            "errors": valid_params["errors"],
                        }
                    )

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error archiving items: {e}")
        return Response(
            {"errors": ["Failed to archive items."]},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# -----------------------------------------------------------------------------------------------------------------------------
# Utils items
# -----------------------------------------------------------------------------------------------------------------------------

def create_item_record(data, user):
    try:
        item_id = data.get("item_id", randomstr())
        logger.info(f"got the id: {item_id}")
        item_data = {
            "item_id": item_id,
            "created_user": user,
        }

        # Add base fields
        for field, config in BASE_FIELDS.items():
            if field in data and field != "item_id":
                
                # Upload file
                if field in ["cover_photo"]:
                    file = None
                    file = create_file_object_from_upload_data(data[field], user)
                    if file:
                        item_data[field] = file

                # All other fields
                else:
                    item_data[field] = data[field]

        # Remove None values from dictionary
        item_data = {k: v for k, v in item_data.items() if v is not None}

        logger.info(f"item data: {item_data}")
        item = Item.objects.create(**item_data)

        return {
            "success": True,
            "item": item,
        }
    except Exception as e:
        logger.error(f"Error creating item record: {e}")
        return {
            "success": False,
            "errors": ["Error creating the item record"],
        }


def update_item_record(item, data, user):
    try:
        updated_fields = []

        for field, config in BASE_FIELDS.items():
            if field in data and field != "item_id":
                
                if field in ["cover_photo"]:
                    file = None
                    file = create_file_object_from_upload_data(data[field], user)

                    if file:
                        setattr(item, field, file)
                
                # All other fields
                else:
                    setattr(item, field, data[field])
                
                updated_fields.append(field)

        if updated_fields:
            item.save(update_fields=updated_fields)

        return {
            "success": True,
            "item": item,
        }

    except Exception as e:
        logger.error(f"Error {e}")
        return {
            "success": False,
            "errors": ["Error updating the item record"],
        }
