from django.urls import path

from .views import ping_view


app_name = 'watcher'


urlpatterns = [
    path('ping', ping_view, name='ping'),
]
