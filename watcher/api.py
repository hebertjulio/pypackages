import re

from django.conf import settings

from requests import get as rget

from .resume import text_resume


class LibrariesIOError(Exception):

    def __init__(self, package, error):
        message = '[libraries.io] package: %s, error: %s' % (package, error)
        super().__init__(message)


class LibrariesIO:

    access_token = settings.LIBRARIESIO_ACCESS_TOKEN

    @staticmethod
    def get_info(platform, package):
        resp = rget(
            'https://libraries.io/api/%s/%s?api_key=%s' % (
                platform, package, LibrariesIO.access_token))

        if 200 <= resp.status_code >= 299:
            raise resp.raise_for_status()

        info = resp.json()

        if 'error' in info and info['error']:
            raise LibrariesIOError(package, info['error'])

        description = ''
        if 'description' in info:
            description = info['description'] or ''
            description = text_resume(description, 255)

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

        if 'repository_url' in info:
            regex = r'(?:http[s]?://)?(github|gitlab|bitbucket)'
            match = re.match(regex, homepage)
            if match:
                homepage = info['repository_url'] or ''

        if not homepage:
            if 'package_manager_url' in info:
                homepage = info['package_manager_url'] or ''

        rank = 0
        if 'rank' in info:
            rank = info['rank'] or 0

        return {
            'description': description, 'repository': repository,
            'homepage': homepage, 'keywords': keywords, 'rank': rank,
        }
