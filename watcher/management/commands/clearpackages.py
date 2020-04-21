import sys

from django.core.management.base import BaseCommand
from django.conf import settings

from watcher.models import Package


class Command(BaseCommand):
    help = 'Delete 1000 pacakges when 8000 packages was inserted'

    def handle(self, *args, **options):
        try:
            Command.processing()
        except KeyboardInterrupt:
            sys.exit(0)

    @staticmethod
    def processing():
        count = Package.objects.all().count()
        if count <= 8000:
            return
        packages = Package.objects.filter(
            status__in=(Package.STATUS.fail, Package.STATUS.done,),
            rank__lt=settings.MIN_RANK).values_list('pk').order_by(
                'rank', '-created')[0:1000]
        deleted, _ = Package.objects.filter(pk__in=packages).delete()
        print('package(s) deleted: %d' % deleted)
