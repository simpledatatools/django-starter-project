from files.models import *
from backend.models import *
from accounts.models import *
from core.utils import *

import logging

logger = logging.getLogger("Django Starter Project")


# Get the user IP Address
def get_ip_address(request):
    req_headers = request.META
    x_forwarded_for_value = req_headers.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for_value:
        ip_addr = x_forwarded_for_value.split(",")[-1].strip()
    else:
        ip_addr = req_headers.get("REMOTE_ADDR")
    return ip_addr


# Example user log
'''
def create_user_log(
    request,
    event=None,
    content=None,
    data=None,
    valid=True,
    error=None,
):

    user = None
    if request.user:
        if not request.user.is_anonymous:
            user = request.user
        else:
            user = None

    ip_address = get_ip_address(request)
    view_name = request.resolver_match.view_name
    path = request.path
    full_path = request.get_full_path()

    user_log = UserLog()
    user_log.user_log_id = randomlongstr()
    user_log.user = user
    user_log.view_name = view_name
    user_log.event = event
    user_log.ip_address = ip_address
    user_log.path = path
    user_log.full_path = full_path
    user_log.error = error
    user_log.data = data
    user_log.valid = valid
    user_log.save()
'''


