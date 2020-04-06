from django.core.management.base import BaseCommand
from django.contrib.admin.models import LogEntry


class Command(BaseCommand):
    help = 'Clean recent actions logging.'

    def handle(self, *args, **options):
        LogEntry.objects.all().delete()
