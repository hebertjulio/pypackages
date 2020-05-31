import sys
import re

from django.core.management.base import BaseCommand

from requests import get as rget
from xmltodict import parse as xmlparse
from dateutil import parser

from packages.models import Project


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
            Command.add_project(info)

    @staticmethod
    def add_project(info):
        project, _ = Project.objects.get_or_create(
            name=info['name']
        )
        if info['release'] > project.release:
            project.release = info['release']
            project.status = Project.STATUS.new
            project.modified = info['pubdate']
            project.save()

    @staticmethod
    def get_updates():
        resp = rget('https://pypi.org/rss/updates.xml')
        json = xmlparse(resp.text)
        for item in json['rss']['channel']['item']:
            regex = r'^(.+)\s(.+)$'
            matches = re.search(regex, item['title'])
            name = matches.group(1)
            release = matches.group(2)
            pubdate = parser.parse(item['pubDate'])
            yield {
                'name': name, 'release': release,
                'pubdate': pubdate,
            }
