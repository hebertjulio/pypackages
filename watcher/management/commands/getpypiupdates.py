import sys
import re

from django.core.management.base import BaseCommand

from requests import get as rget
from xmltodict import parse as xmlparse

from watcher.models import Package, Release
from watcher.resume import text_resume


class Command(BaseCommand):
    help = 'Read http://pypi.org/rss/updates.xml to catch new releases'

    def handle(self, *args, **options):
        try:
            Command.processing()
        except KeyboardInterrupt:
            sys.exit(0)

    @staticmethod
    def processing():
        for item in Command.get_updates():
            try:
                package = Package.objects.get(
                    programming_language=item['programming_language'],
                    name__iexact=item['name'])
            except Package.DoesNotExist:
                package = Package.objects.create(
                    name=item['name'],
                    programming_language=item['programming_language'],
                    description=item['description'],
                    keywords=item['keywords'],
                    homepage=item['homepage'])
            if package.status != Package.STATUS.fail:
                Release.objects.get_or_create(
                    name=item['release'], package=package,
                )

    @staticmethod
    def get_updates():
        resp = rget('https://pypi.org/rss/updates.xml')
        json = xmlparse(resp.text)
        for item in json['rss']['channel']['item']:
            # get package name and release
            regex = r'^(.+)\s(.+)$'
            matches = re.search(regex, item['title'])
            name = matches.group(1)
            release = matches.group(2)

            # skip no stable releases
            regex = r'(?:dev|rc)\d+'
            match = re.match(regex, release)

            if match is None:
                regex = r'^(.+)(?:%s/)$' % release
                matches = re.search(regex, item['link'])
                homepage = matches.group(1)

                description = item['description'] or ''
                description = text_resume(description, 255, ' ')

                yield {
                    'name': name, 'release': release, 'keywords': '',
                    'homepage': homepage, 'description': description,
                    'programming_language': Package.PROGRAMMING_LANGUAGE.python,
                }
