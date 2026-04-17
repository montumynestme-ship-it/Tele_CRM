from django.http import HttpResponse

def health_check(request):
    """
    Extremely lightweight healthcheck.
    Returns HTTP 200 'ok' without any JSON overhead or app logic.
    """
    return HttpResponse("ok", content_type="text/plain", status=200)
