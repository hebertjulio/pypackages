import sys
import re

from django.core.management.base import BaseCommand
from django.conf import settings

import tweepy

from watcher.models import Package
from watcher.resume import text_resume


MAX_TWEET_SIZE = 280


class Command(BaseCommand):
    help = 'Tweet new releases of packages by twitter accounts'

    text_template = (
        'The release of %s package %s is now available. 🥳\n\n%s'
    )

    chars = '@/_-#$%*!()&=+[]:;? '
    trans = str.maketrans(
        dict(zip(list(chars), [None for v in range(len(chars))])))

    def handle(self, *args, **options):
        try:
            Command.processing()
        except KeyboardInterrupt:
            sys.exit(0)

    @staticmethod
    def processing():
        for account in Command.get_accounts():
            packages = Package.objects.filter(
                programming_language=account['programming_language'],
                status=Package.STATUS.done,
                has_new_release=True,
            ).order_by('rank', '-modified')
            for package in packages:
                package.has_new_release = False
                package.save()
                if package.rank >= settings.MIN_RANK:
                    continue
                regex = package.stable_release_regex
                if regex:
                    match = re.search(regex, package.last_release)
                    if match is None:
                        continue
                Command.write_tweets(package, account['api'])
                break

    @staticmethod
    def get_accounts():
        if 'TWITTER_ACCOUNTS' in settings:
            for programming_language in ['python']:
                if programming_language in settings['TWITTER_ACCOUNTS']:
                    secrets = settings[
                        'TWITTER_ACCOUNTS'][programming_language]
                    auth = tweepy.OAuthHandler(
                        secrets['API_KEY'],
                        secrets['API_SECRET']
                    )
                    auth.set_access_token(
                        secrets['ACCESS_TOKEN'],
                        secrets['ACCESS_TOKEN_SECRET']
                    )
                    yield {
                        'programming_language': programming_language,
                        'api': tweepy.API(auth)
                    }

    @staticmethod
    def write_tweets(package, api):
        package_name = package.name
        description = package.description.strip()
        homepage = package.homepage
        last_release = package.last_release

        hashtags = sorted(
            ['#' + keyword
                for keyword in package.keywords.split(',')
                if keyword.strip()],
            key=len)

        while True:
            tweet_text = (
                'The release of %s package %s is now available. 🥳'
                '\n\n%s%s\n\n%s') % (
                    package_name, last_release,
                    '%s\n' % description if description else '',
                    homepage, ' '.join(hashtags))

            if len(tweet_text) < MAX_TWEET_SIZE:
                api.update_status(tweet_text)
                break

            if len(hashtags) > 2:
                hashtags = hashtags[:-1]
            else:
                description = text_resume(
                    description, MAX_TWEET_SIZE, ' ',
                    oneslice=False) + '...'
