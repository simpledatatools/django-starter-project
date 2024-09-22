from django.http import HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /static/",
        "Disallow: /admin/",
        "Disallow: /internal/",
        "Disallow: /files/",
        "Disallow: /fetch/",
        "Disallow: /webhooks/",
        "Disallow: /api/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
