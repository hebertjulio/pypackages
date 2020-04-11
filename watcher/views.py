from django.http import JsonResponse


def ping_view(request):
    """ Endpoit to wakeup dyno. """
    return JsonResponse({'resp': 'pong'})
