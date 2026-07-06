from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        "status": "ok",
        "message": "InterviewLab backend is running"
    })