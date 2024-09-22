from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import Http404
from django.template import loader
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import logout
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import urllib.parse
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

import json
from operator import itemgetter

# Dates and
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone

# Settings
from django.conf import settings

# Models
from accounts.models import *
from backend.models import *

# Utils
from core.utils import *
from backend.utils import *

# Tasks
from files.tasks import *
from messaging.tasks import *

import time
from django.apps import apps

import logging

logger = logging.getLogger("Django Starter Project")


def landing(request):
    context = {}
    return render(request, "website/landing.html", context=context)


def terms(request):
    context = {}
    return render(request, "website/terms.html", context=context)


def privacy(request):
    context = {}
    return render(request, "website/privacy.html", context=context)


def about(request):
    context = {}
    return render(request, "website/about.html", context=context)


