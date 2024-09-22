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

# Custom decorators
from backend.decorators import *

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

@login_required
def items(request):
    user = request.user
    context = {}
    return render(request, "app/items/list.html", context=context)


@login_required
def item_details(request, item_id):
    user = request.user
    item = Item.objects.filter(item_id=item_id, status='active').first()
    if not item:
        return redirect('error_404')
    context = {'item': item}
    return render(request, "app/items/details.html", context=context)


@login_required
def item_settings(request, item_id):
    user = request.user
    item = Item.objects.filter(item_id=item_id, status='active').first()
    if not item:
        return redirect('error_404')
    context = {'item': item}
    return render(request, "app/items/settings.html", context=context)


@login_required
def add_item(request):
    user = request.user
    return render(request, "app/items/add.html")


@login_required
def edit_item(request, item_id):
    user = request.user
    item = Item.objects.filter(item_id=item_id, status='active').first()
    if not item:
        return redirect('error_404')
    context = {'item': item}
    return render(request, "app/items/edit.html", context=context)


# Fetch/GET call to get a list of items
@login_required
def fetch_items(request):
    user = request.user
    search_term = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 25)

    # Filter the items
    items = Item.objects.filter(status='active').order_by('name')

    # Filter items based on the search term
    if search_term:
        items = items.filter(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(address__icontains=search_term) |
            Q(phone_number__icontains=search_term)
        ).order_by('name').values()

    # Paginate the results
    paginator = Paginator(items, page_size)
    
    try:
        items_page = paginator.page(page)
    except PageNotAnInteger:
        items_page = paginator.page(1)
    except EmptyPage:
        items_page = paginator.page(paginator.num_pages)

    items_html = [render_to_string('app/items/list-item.html', {'item': item}) for item in items_page]

    response_data = {
        'items_html': items_html,
        'page': items_page.number,
        'pages': paginator.num_pages,
        'total_records': paginator.count,
    }

    return JsonResponse(response_data)


# Fetch/GET call to get individual item details
@login_required
def fetch_item_details(request, item_id):
    user = request.user
    item = Item.objects.filter(item_id=item_id, status='active').first()
    if not item:
        return JsonResponse({'error': 'Item not found'}, status=404)

    # Get the item details
    item_details =  {
        'name': item.name, 
        'status': item.status
    }
    return JsonResponse({'item': item_details})


# Fetch/POST call for adding a item
@login_required
def fetch_add_item(request):
    user = request.user
    if request.method == 'POST':
        item_id = randomstr()
        name = request.POST.get('name')
        created_user = user
        item = Item.objects.create(
            item_id=item_id, 
            name=name, 
            created_user=created_user
        )
        
        return JsonResponse({'item': {'name': item.name}}, status=201)
    return JsonResponse({'error': 'Invalid data'}, status=400)


# Fetch/PUT call for editing a item
@login_required
def fetch_edit_item(request, item_id):
    user = request.user
    item = Item.objects.filter(item_id=item_id, status='active').first()
    if not item:
        return JsonResponse({'error': 'Item not found'}, status=404)
    if request.method == 'POST':
        name = request.POST.get('name')
        # Update the item values
        item.name = name
        item.save()
        return JsonResponse({'item': {}}, status=200)
    return JsonResponse({'error': 'Invalid data'}, status=400)


# Fetch/PUT call for archiving a item
@login_required
def fetch_archive_item(request, item_id):
    user = request.user
    item = Item.objects.filter(item_id=item_id, status='active').first()
    if not item:
        return JsonResponse({'error': 'Item not found'}, status=404)
    item.status = 'archived'
    item.save()
    return JsonResponse({'message': 'Item archived successfully'})

