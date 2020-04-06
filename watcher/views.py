from django.http import JsonResponse


def ping_view(request):
    return JsonResponse({'resp': 'pong'})
