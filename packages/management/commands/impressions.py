import sys
import re

from django.core.management.base import BaseCommand
from django.conf import settings

import tweepy

from ...models import Project


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            self.processing()
        except KeyboardInterrupt:
            sys.exit(0)

    @classmethod
    def processing(cls):
        api = cls.get_api('python')
        cursor = tweepy.Cursor(api.user_timeline)
        for status in cursor.items():
            match = re.match(r'^The release of (\w+)', status.text)
            if not match:
                continue
            try:
                project = Project.objects.get(name=match.group(1))
                project.favorite_count += status.favorite_count
                project.retweet_count += status.retweet_count
            except Project.DoesNotExist:
                pass

    @classmethod
    def get_api(cls, account):
        if ('TWITTER_ACCOUNTS' not in settings
                or account not in settings['TWITTER_ACCOUNTS']):
            return
        secrets = settings['TWITTER_ACCOUNTS'][account]
        auth = tweepy.OAuthHandler(secrets['API_KEY'], secrets['API_SECRET'])
        auth.set_access_token(
            secrets['ACCESS_TOKEN'], secrets['ACCESS_TOKEN_SECRET'])
        return tweepy.API(auth)
