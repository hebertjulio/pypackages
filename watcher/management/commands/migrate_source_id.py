import sys

from django.core.management.base import BaseCommand

from watcher.models import Package


RELEASE_MIN_AGE = 1  # days


class Command(BaseCommand):
    help = 'Migrate repository owner and repository name to source id format.'

    def handle(self, *args, **options):
        try:
            for package in Package.objects.all():
                package.source_id = (
                    package.repository_owner + '/' + package.repository_name)
                package.save()
        except KeyboardInterrupt:
            sys.exit(0)
