import sys
import re

from django.core.management.base import BaseCommand
from django.conf import settings

from requests import get as rget
from xmltodict import parse as xmlparse
from dateutil import parser

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
        for info in Command.get_updates():
            package = Command.get_or_create_package(info)
            if (package.status == Package.STATUS.new
                    or package.rank >= settings.MIN_RANK):
                Command.create_or_update_release(
                    info['release'], info['pubdate'], package)

    @staticmethod
    def get_or_create_package(info):
        try:
            package = Package.objects.get(
                programming_language=info['programming_language'],
                name__iexact=info['package'])
        except Package.DoesNotExist:
            package = Package.objects.create(
                name=info['package'],
                programming_language=info['programming_language'],
                description=info['description'],
                keywords=info['keywords'],
                homepage=info['homepage'])
        return package

    @staticmethod
    def create_or_update_release(release, pubdate, package):
        try:
            obj = Release.objects.get(package=package)
            if release > obj.name:
                obj.status = Release.STATUS.new
                obj.name = release
                obj.created = pubdate
                obj.save()
        except Release.DoesNotExist:
            Release.objects.create(
                name=release, package=package,
                created=pubdate, modified=pubdate
            )

    @staticmethod
    def get_updates():
        resp = rget('https://pypi.org/rss/updates.xml')
        json = xmlparse(resp.text)
        for item in json['rss']['channel']['item']:
            # get package name and release
            regex = r'^(.+)\s(.+)$'
            matches = re.search(regex, item['title'])
            package = matches.group(1)
            release = matches.group(2)

            # skip no stable releases
            regex = r'(?:dev|rc)\d+'
            match = re.search(regex, release)

            if match is None:
                regex = r'^(.+)(?:%s/)$' % release
                matches = re.search(regex, item['link'])
                homepage = matches.group(1)

                description = item['description'] or ''
                description = text_resume(description, 255, ' ')

                pubdate = parser.parse(item['pubDate'])

                yield {
                    'package': package, 'release': release, 'keywords': '',
                    'homepage': homepage, 'description': description,
                    'programming_language':
                        Package.PROGRAMMING_LANGUAGE.python,
                    'pubdate': pubdate
                }
