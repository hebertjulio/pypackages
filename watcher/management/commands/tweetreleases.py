import sys

from django.core.management.base import BaseCommand
from django.conf import settings

import tweepy

from watcher.models import Package, Release


MIN_RANK = 1


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
            releases = Release.objects.filter(
                status=Release.STATUS.new, package__rank__gte=MIN_RANK,
                package__programming_language=account['programming_language'],
                package__status=Package.STATUS.done
            ).order_by('created')[0:1]
            for release in releases:
                Command.write_tweets(release, account['api'])

        # put done all releases of packages with rank less than 10
        Release.objects.filter(package__rank__lt=MIN_RANK).update(
            status=Release.STATUS.done)

    @staticmethod
    def get_accounts():
        if 'TWITTER_ACCOUNTS' in settings:
            for programming_language in ['python', 'javascript', 'css']:
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
    def write_tweets(release, api):
        package = release.package.name
        description = release.package.description.strip()
        homepage = release.package.homepage

        hashtags = ' '.join(sorted(
            ['#' + keyword
                for keyword in release.package.keywords.split(',')
                if keyword.strip()],
            key=len))

        while True:
            tweet_text = (
                'The release of %s package %s is now available. 🥳'
                '\n\n%s%s\n\n%s') % (
                    package, release.name,
                    '%s\n' % description if description else '',
                    homepage, hashtags)

            if len(tweet_text) < 280:
                print(tweet_text)
                # api.update_status(tweet_text.strip())
                break

            if len(hashtags) > 5:
                hashtags = hashtags[:-1]
                continue

            description = description.split(' ')
            description = '%s...' % (
                ' '.join(description[:-1]))

        release.status = Release.STATUS.done
        release.save()
