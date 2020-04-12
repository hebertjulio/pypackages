import sys
import re

from django.core.management.base import BaseCommand

from json.decoder import JSONDecodeError
from requests.exceptions import RequestException

from watcher.models import Package, Release
from watcher.sources import GithubSource, PyPiSource
from watcher.services import send_manually_exception_email


class Command(BaseCommand):
    help = 'Watch for new releases in code hosting.'

    def handle(self, *args, **options):
        try:
            sources = {
                'github': GithubSource(),
                'pypi': PyPiSource(),
            }
            Command.processing(sources)
        except KeyboardInterrupt:
            sys.exit(0)

    @staticmethod
    def processing(sources):
        packages = Package.objects.all().order_by('source_type')
        for package in packages:
            try:
                source = sources[package.source_type]
                info = source.get_info(package)

                description = re.sub(
                    r':\w+:', '', info['description']
                ).encode('ascii', 'ignore').decode('ascii').strip()

                while True:
                    if len(description) < 255:
                        break
                    description = description.split(' ')
                    description = ' '.join(description[:-1]) + '...'

                package.description = description
                package.hashtags = info['hashtags']
                package.site_url = info['site_url']

                package.save()

                Command.add_release(info['releases'], package)
            except RequestException:
                subject = '[watch_releases] package: ' + package.name
                send_manually_exception_email(subject)
            except JSONDecodeError:
                subject = '[watch_releases] package: ' + package.name
                send_manually_exception_email(subject)

    @staticmethod
    def add_release(releases, package):
        for release in releases:
            release_exists = Release.objects.filter(
                name=release['name'], package=package
            ).exists()
            if release_exists is False:
                Release.objects.create(**{
                    **release, 'package': package
                })
