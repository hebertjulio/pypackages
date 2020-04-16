import re

from django.conf import settings

from requests import get as rget


class LibrariesIO:

    @staticmethod
    def get_info(platform, package):
        access_token = settings.LIBRARIESIO_ACCESS_TOKEN
        resp = rget(
            'https://libraries.io/api/%s/%s?api_key=%s' % (
                platform, package, access_token))

        info = resp.json()

        description = ''
        if 'description' in info:
            description = info['description'] or ''

        repository = ''
        if 'repository_url' in info:
            repository = info['repository_url'] or ''

        keywords = []
        if 'keywords' in info:
            keywords = info['keywords'] or []

        homepage = ''
        if 'homepage' in info:
            if info['homepage']:
                homepage = info['homepage'] or ''

        if 'package_manager_url' in info:
            regex = r'(?:http[s]?://)?(github|gitlab|bitbucket)'
            match = re.match(regex, homepage)
            if match:
                print(homepage)
                homepage = info['package_manager_url']

        rank = 0
        if 'rank' in info:
            rank = info['rank'] or 0

        return {
            'description': description, 'repository': repository,
            'homepage': homepage, 'keywords': keywords, 'rank': rank,
        }
