import sys
import time

from django.core.management.base import BaseCommand

from requests.exceptions import HTTPError

from watcher.api import LibrariesIO, LibrariesIOError
from watcher.models import Package
from watcher.resume import text_resume


MAX_RETRY = 5


class Command(BaseCommand):
    help = 'Get info in Libraries.io to update new and outdated packages'

    trans = str.maketrans({
        '-': None, '_': None, ' ': None, '.': None
    })

    def handle(self, *args, **options):
        try:
            Command.processing()
        except KeyboardInterrupt:
            sys.exit(0)

    @staticmethod
    def processing():
        packages = Package.objects.filter(
            status=Package.STATUS.new).order_by('modified')
        for package in packages:
            package.message = ''
            retry = 0
            platform = 'pypi'
            while True:
                try:
                    error = None
                    info = LibrariesIO.get_info(platform, package.name)
                except HTTPError as e:
                    if retry < MAX_RETRY:
                        retry += 1
                        if e.response.status_code == 429:
                            time.sleep(65)
                            continue
                        if e.response.status_code == 404:
                            time.sleep(10)
                            continue
                    error = e
                except LibrariesIOError as e:
                    error = e
                break

            if error is not None:
                package.message = error
                package.status = Package.STATUS.fail
                package.save()
                continue

            keywords = ','.join(list(dict.fromkeys([
                keyword.translate(Command.trans).lower()
                for keyword in [
                    Package.PROGRAMMING_LANGUAGE.python,
                    package.name,
                ] + info['keywords']])
            ))

            package.keywords = text_resume(keywords, 255, ',')

            if info['description']:
                description = info['description']
                description = text_resume(description, 255, ' ')

            if info['homepage']:
                package.homepage = info['homepage']

            package.repository = info['repository']
            package.rank = info['rank']
            package.status = Package.STATUS.done
            package.save()
