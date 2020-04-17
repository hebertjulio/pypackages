import sys

from django.core.management.base import BaseCommand
from django.conf import settings

from watcher.models import Package


class Command(BaseCommand):
    help = 'Clear packages that failed or no min rank'

    def handle(self, *args, **options):
        try:
            Command.processing()
        except KeyboardInterrupt:
            sys.exit(0)

    @staticmethod
    def processing():
        # delete all fail packages
        Package.objects.filter(
            status=Package.STATUS.fail
        ).delete()

        # delete all packages with rank less than MIN_RANK
        Package.objects.filter(
            status=Package.STATUS.done,
            rank__lt=settings.MIN_RANK
        ).delete()
