from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse({"status": "unhealthy", "error": "Database connection failed"}, status=500)

    return JsonResponse({"status": "ok"})

