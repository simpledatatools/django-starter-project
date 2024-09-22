from django.shortcuts import render


def error_401(request, exception=None):
    data = {}
    return render(request, "app/errors/401.html", status=401)

def error_403(request, exception=None):
    data = {}
    return render(request, "app/errors/403.html", status=403)


def error_404(request, exception=None):
    data = {}
    return render(request, "app/errors/404.html", status=404)

def error_500(request):
    return render(request, "app/errors/500.html", status=500)
