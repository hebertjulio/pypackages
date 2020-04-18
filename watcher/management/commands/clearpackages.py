import sys
import datetime

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone

from watcher.models import Package


class Command(BaseCommand):
    help = 'Clear old packages that failed or no min rank'

    def handle(self, *args, **options):
        try:
            Command.processing()
        except KeyboardInterrupt:
            sys.exit(0)

    @staticmethod
    def processing():
        now = timezone.now()
        delta = now - datetime.timedelta(days=90)
        # delete all fail packages
        Package.objects.filter(
            status=Package.STATUS.fail,
            created__lte=delta,
        ).delete()
        # delete all packages with rank less than MIN_RANK
        Package.objects.filter(
            status=Package.STATUS.done,
            created__lte=delta,
            rank__lt=settings.MIN_RANK,
        ).delete()
