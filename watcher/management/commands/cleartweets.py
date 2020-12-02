import sys
import re

from django.core.management.base import BaseCommand
from django.conf import settings

import tweepy


class Command(BaseCommand):
    help = 'Delete duplicate old tweets'

    def handle(self, *args, **options):
        try:
            api = self.get_api()
            if api:
                self.processing(api)
        except KeyboardInterrupt:
            sys.exit(0)

    @classmethod
    def processing(cls, api):
        projects = {}
        pattern = re.compile(r'^The release of ([\w\-\.\_]+) ')
        statuses = tweepy.Cursor(api.user_timeline).items()
        for status in statuses:
            match = pattern.findall(status.text)
            if match:
                project = match[0]
                if project in projects.keys():
                    projects[project].append(status.id)
                else:
                    projects.setdefault(project, [status.id])
        for project, ids in projects.items():
            if len(ids) > 1:
                for id_ in ids[1:]:
                    api.destroy_status(id_)

    @classmethod
    def get_api(cls):
        if 'TWITTER_ACCOUNTS' in settings:
            secrets = settings[
                'TWITTER_ACCOUNTS']['python']
            auth = tweepy.OAuthHandler(
                secrets['API_KEY'],
                secrets['API_SECRET']
            )
            auth.set_access_token(
                secrets['ACCESS_TOKEN'],
                secrets['ACCESS_TOKEN_SECRET']
            )
            return tweepy.API(auth)
