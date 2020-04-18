import sys
import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from watcher.models import Release


class Command(BaseCommand):
    help = 'Clear all old releases'

    def handle(self, *args, **options):
        try:
            Command.processing()
        except KeyboardInterrupt:
            sys.exit(0)

    @staticmethod
    def processing():
        now = timezone.now()
        delta = now - datetime.timedelta(days=2)
        # delete all old releases
        Release.objects.filter(
            created__lte=delta
        ).delete()
