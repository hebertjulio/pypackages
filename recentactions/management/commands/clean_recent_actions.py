import time

from django.core.management.base import BaseCommand
from django.contrib.admin.models import LogEntry


class Command(BaseCommand):
    help = 'Clean recent actions logging.'

    def handle(self, *args, **options):
        start_time = time.time()
        LogEntry.objects.all().delete()
        print("clean_recent_actions: %s seconds" % (time.time() - start_time))
