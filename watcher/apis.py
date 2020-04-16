from django.conf import settings

from requests import get as rget


class LibrariesIO:
    def get_info(platform, package):
        access_token = settings.LIBRARIESIO_ACCESS_TOKEN
        resp = rget(
            'https://libraries.io/api/%s/%s?api_key=%s' % (
                platform, package, access_token))
        info = resp.json()

        return {
            'description': info['description'] or '',
            'repository': info['repository_url'] or '',
            'homepage': info['homepage'] or info['package_manager_url'],
            'keywords': info['keywords'] or [],
            'rank': info['rank'],
        }
