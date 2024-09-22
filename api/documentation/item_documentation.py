from rest_framework import serializers
from drf_spectacular.utils import inline_serializer

# Helper function to extract fields from a serializer and convert them to a standard dict
def extract_fields(serializer_class, include_fields=None, required_fields=None):
    if include_fields:
        fields = {k: v for k, v in serializer_class().fields.items() if k in include_fields}
    else:
        fields = dict(serializer_class().fields)

    if required_fields:
        for field in required_fields:
            if field in fields:
                fields[field].required = True

    return fields

# Base Item Schema for response
def base_item_schema(include_fields=None):
    class BaseItemSerializer(serializers.Serializer):
        item_id = serializers.CharField()
        name = serializers.CharField()
        address = serializers.CharField()
        date_of_birth = inline_serializer(
            name='DateTimeProperties',
            fields={
                "year": serializers.IntegerField(),
                "month": serializers.IntegerField(),
                "day": serializers.IntegerField(),
                "hour": serializers.IntegerField(),
                "minute": serializers.IntegerField(),
                "second": serializers.IntegerField(),
                "timezone": serializers.CharField(),
            }
        )
        registration_date = inline_serializer(
            name='DateTimeProperties',
            fields={
                "year": serializers.IntegerField(),
                "month": serializers.IntegerField(),
                "day": serializers.IntegerField(),
                "hour": serializers.IntegerField(),
                "minute": serializers.IntegerField(),
                "second": serializers.IntegerField(),
                "timezone": serializers.CharField(),
            }
        )
        phone_number = serializers.CharField()
        age = serializers.IntegerField()
        gender = serializers.ChoiceField(choices=["male", "female"])
        created_user = serializers.CharField()
        created_at = inline_serializer(
            name='DateTimeProperties',
            fields={
                "year": serializers.IntegerField(),
                "month": serializers.IntegerField(),
                "day": serializers.IntegerField(),
                "hour": serializers.IntegerField(),
                "minute": serializers.IntegerField(),
                "second": serializers.IntegerField(),
                "timezone": serializers.CharField(),
            }
        )
        updated_at = inline_serializer(
            name='DateTimeProperties',
            fields={
                "year": serializers.IntegerField(),
                "month": serializers.IntegerField(),
                "day": serializers.IntegerField(),
                "hour": serializers.IntegerField(),
                "minute": serializers.IntegerField(),
                "second": serializers.IntegerField(),
                "timezone": serializers.CharField(),
            }
        )
        # Add other fields here

    fields = extract_fields(BaseItemSerializer, include_fields=include_fields)
    return inline_serializer(name='BaseItemSerializer', fields=fields)

# Item schema for requests (add, single update, and bulk update)
def request_item_schema(required_fields=['name'], include_fields=None):
    class RequestItemSerializer(serializers.Serializer):
        item_id = serializers.CharField(required=False)
        name = serializers.CharField()
        # Add other fields here

    fields = extract_fields(RequestItemSerializer, include_fields=include_fields, required_fields=required_fields)
    return inline_serializer(name='RequestItemSerializer', fields=fields)

# Item schema for archive response
def archive_item_schema():
    class ArchiveItemSerializer(serializers.Serializer):
        item_id = serializers.CharField()

    fields = extract_fields(ArchiveItemSerializer)
    return inline_serializer(name='ArchiveItemSerializer', fields=fields)

# Item list response object
item_list_response_schema = inline_serializer(
    name='ItemListResponseSerializer',
    fields={
        "data": serializers.ListSerializer(child=base_item_schema()),
        "page": serializers.IntegerField(),
        "pages": serializers.IntegerField(),
        "records_count": serializers.IntegerField(),
    }
)

# Item response object
item_response_schema = base_item_schema()

# Location Ping Count Response
item_count_response_schema = inline_serializer(
    name='ItemCountResponseSerializer',
    fields={
        "count": serializers.IntegerField(),
    }
)

# Adding response object
item_not_added_entry_schema = inline_serializer(
    name='ItemNotAddedEntrySerializer',
    fields={
        "index": serializers.IntegerField(),
        "submitted_object": request_item_schema(),
        "errors": serializers.ListSerializer(child=serializers.CharField()),
    }
)

add_items_response_schema = inline_serializer(
    name='AddItemsResponseSerializer',
    fields={
        "items_added": serializers.ListSerializer(child=base_item_schema()),
        "items_not_added": serializers.ListSerializer(child=item_not_added_entry_schema),
    }
)

# Updating response object
item_not_updated_entry_schema = inline_serializer(
    name='ItemNotUpdatedEntrySerializer',
    fields={
        "index": serializers.IntegerField(),
        "submitted_object": request_item_schema(),
        "errors": serializers.ListSerializer(child=serializers.CharField()),
    }
)

update_items_response_schema = inline_serializer(
    name='UpdateItemsResponseSerializer',
    fields={
        "items_updated": serializers.ListSerializer(child=base_item_schema()),
        "items_not_updated": serializers.ListSerializer(child=item_not_updated_entry_schema),
    }
)

# Archiving response object
item_not_archived_entry_schema = inline_serializer(
    name='ItemNotArchivedEntrySerializer',
    fields={
        "index": serializers.IntegerField(),
        "submitted_object": request_item_schema(include_fields=["item_id"]),
        "errors": serializers.ListSerializer(child=serializers.CharField()),
    }
)

archive_items_response_schema = inline_serializer(
    name='ArchiveItemsResponseSerializer',
    fields={
        "items_archived": serializers.ListSerializer(child=archive_item_schema()),
        "items_not_archived": serializers.ListSerializer(child=item_not_archived_entry_schema),
    }
)

destroy_items_response_schema = inline_serializer(
    name='DestroyItemsResponseSerializer',
    fields={
        "items_archived": serializers.ListSerializer(child=archive_item_schema()),
    }
)

# Generate schemas for add and update operations
item_add_schema = request_item_schema(required_fields=["name"])
single_item_update_schema = request_item_schema(
    required_fields=["name"], include_fields=["name", "cover_photo"]
)
bulk_item_update_schema = request_item_schema(
    required_fields=["item_id", "name"], include_fields=["item_id", "name", "cover_photo"]
)
item_archive_schema = request_item_schema(
    required_fields=["item_id"], include_fields=["item_id"]
)

# Function to create a request body schema that includes 'items' key
def create_items_key_request_body_schema(base_schema):
    return inline_serializer(
        name='ItemsKeyRequestBodySerializer',
        fields={
            "items": serializers.ListSerializer(child=base_schema)
        },
        required=['items']
    )

# Generate request body schemas with 'items' key
item_add_request_body = create_items_key_request_body_schema(item_add_schema)
item_bulk_update_request_body = create_items_key_request_body_schema(bulk_item_update_schema)
item_archive_request_body = create_items_key_request_body_schema(item_archive_schema)

# Item response schema
item_schema = base_item_schema()
