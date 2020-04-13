import re

from django.utils.dateparse import parse_datetime
from django.utils import timezone

import requests

from .github import GithubClient


class PyPiSource:

    gql_query = '''{
        repository(owner: "%s", name: "%s") {
            topics:repositoryTopics(first: 10) {
                nodes {
                  topic {
                    name
                  }
                }
            }
        }
    }'''

    RELEASE_MIN_AGE = 15

    now = timezone.now()

    @staticmethod
    def get_info(package):
        info = PyPiSource.request(package)

        releases = PyPiSource.get_releases(
            info['releases'], package.release_regex)

        tags = PyPiSource.get_topics(
                info['info']['project_urls']
        )

        return {
            'description': info['info']['summary'] or '',
            'site_url': info[
                'info']['home_page'] or info[
                'info']['project_url'],
            'tags': tags, 'releases': releases
        }

    @staticmethod
    def request(package):
        resp = requests.get(
            'https://pypi.org/pypi/%s/json' % package.source_id)
        return resp.json()

    @staticmethod
    def get_repository(project_urls):
        for url in project_urls.values():
            matches = re.search(r'github\.com/([\w_-]+/[\w_-]+)', url)
            if matches is not None:
                return matches.group(1)
        return None

    @staticmethod
    def get_topics(project_urls):
        repository = PyPiSource.get_repository(project_urls)
        if repository is not None:
            repository_owner, repository_name = repository.split('/')
            gql_query = PyPiSource.gql_query % (
                repository_owner, repository_name)
            resp = GithubClient.execute(gql_query)
            return [
                node['topic']['name']
                for node in resp['repository']['topics']['nodes']
            ]
        return []

    @staticmethod
    def get_releases(releases, release_regex):
        prefixes = []
        for name in reversed(releases):
            if releases[name]:
                info = releases[name][0]
                created = parse_datetime(info['upload_time_iso_8601'])
                age = abs(PyPiSource.now - created).days
                if age > PyPiSource.RELEASE_MIN_AGE:
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
