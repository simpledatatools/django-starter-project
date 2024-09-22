import os
import django
import time
import random
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.utils import *
from backend.models import *
from channels.layers import get_channel_layer  
from asgiref.sync import async_to_sync 
from accounts.models import *

# Test comment
