from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from backend.models import *


# Example decorator

'''
def validate_param(func):
    @wraps(func)
    def decorator(request, *args, **kwargs):
        param_id = kwargs.get('param_id')
        user = request.user

        # do some stuff here

        request.param = param

        return func(request, *args, **kwargs)
    return decorator
'''