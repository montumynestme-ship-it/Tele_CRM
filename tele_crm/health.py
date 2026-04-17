from django.http import JsonResponse

def health_check(request):
    """
    Extremely lightweight healthcheck path.
    Does not require database or complex imports.
    """
    return JsonResponse({"status": "healthy"}, status=200)
