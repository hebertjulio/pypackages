import re

from django.utils.dateparse import parse_datetime
from django.utils import timezone

import requests


class PyPi:

    RELEASE_MIN_AGE = 15

    now = timezone.now()

    def get_info(self, package):
        info = PyPi.request(package)
        hashtags = PyPi.get_hasttags([], [
                package.programming_language,
                package.name
        ])
        releases = PyPi.get_releases(
            info['releases'], package.release_regex
        )
        return {
            'description': info['info']['summary'] or '',
            'site_url': info[
                'info']['home_page'] or info[
                'info']['project_url'],
            'hashtags': hashtags, 'releases': releases,
        }

    @staticmethod
    def request(package):
        resp = requests.get('https://pypi.org/pypi/%s/json' % package.name)
        return resp.json()

    @staticmethod
    def get_hasttags(topics, extra_topics):
        hashtags = set()
        for topic in topics + extra_topics:
            hashtag = '#' + topic
            hashtag = hashtag.lower()
            hashtag = hashtag.replace('-', '')
            hashtag = hashtag.replace('_', '')
            hashtag = hashtag.replace('@', '')
            hashtag = hashtag.replace('/', '')
            hashtags.add(hashtag)
        return ' '.join(hashtags)

    @staticmethod
    def get_releases(releases, release_regex):
        prefixes = []
        for name in reversed(releases):
            if releases[name]:
                info = releases[name][0]
                created = parse_datetime(info['upload_time_iso_8601'])
                age = abs(PyPi.now - created).days
                if age > PyPi.RELEASE_MIN_AGE:
                    continue
                matches = re.search(release_regex, name)
                if matches is not None:
                    if 0 in prefixes:
                        break
                    prefix = matches.group(2)
                    if prefix in prefixes:
                        continue
                    prefixes.append(prefix)
                    yield {
                        'name': name,
                        'created': created
                    }
