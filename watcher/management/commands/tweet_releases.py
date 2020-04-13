import sys

from django.core.management.base import BaseCommand
from django.conf import settings

import tweepy

from watcher.models import Release


class Command(BaseCommand):
    help = 'Tweet new releases.'

    text_template = (
        'The release of %s package %s is now available. 🥳\n\n%s'
    )

    chars = '@/_-#$%*!()&=+[]:;? '
    trans = str.maketrans(
        dict(zip(list(chars), ['' for v in range(len(chars))])))

    def handle(self, *args, **options):
        try:
            accounts = Command.get_accounts()
            Command.processing(accounts)
        except KeyboardInterrupt:
            sys.exit(0)

    @staticmethod
    def processing(accounts):
        for account in accounts:
            releases = Release.objects.filter(
                package__programming_language=account['programming_language'],
                status=Release.STATUS.new
            ).order_by('created')[0:1]
            if releases:
                Command.write_tweets(releases[0], account['api'])

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
        description = release.package.description
        site_url = release.package.site_url
        version = release.name

        trans = str.maketrans({
            '@': None, '/': None, '-': None,
            '_': None, ' ': None
        })

        hashtags = ' '.join(list(dict.fromkeys([
            '#' + tag.translate(trans)
            for tag in
            release.package.tags.split(',') + [
                release.package.programming_language,
                release.package.name
            ]]))
        )

        while True:
            tweet_text = (
                'The release of %s package %s is now'
                ' available. 🥳\n\n%s%s\n\n%s') % (
                    package, version,
                    '%s\n' % description if description else '',
                    site_url, hashtags
                )
            if len(tweet_text) < 280:
                api.update_status(tweet_text.strip())
                break

            description = description.split(' ')
            description = '%s...' % (
                ' '.join(description[:-1]))

        release.status = Release.STATUS.tweeted
        release.save()
