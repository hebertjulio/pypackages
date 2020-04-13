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

    RELEASE_MIN_AGE = 5

    now = timezone.now()

    @staticmethod
    def get_info(package):
        info = PyPiSource.request(package)

        if not package.code_hosting_repository:
            code_hosting_repository = PyPiSource.get_code_hosting_repository(
                info['info']['project_urls'])
        else:
            code_hosting_repository = package.code_hosting_repository

        if code_hosting_repository is not None:
            tags = PyPiSource.get_code_hosting_topics(
                code_hosting_repository)
        else:
            tags = []

        releases = PyPiSource.get_releases(
            info['releases'], package.release_regex)

        return {
            'description': info['info']['summary'] or '',
            'site_url': info[
                'info']['home_page'] or info[
                'info']['project_url'],
            'tags': tags, 'releases': releases,
            'code_hosting_repository': code_hosting_repository
        }

    @staticmethod
    def request(package):
        resp = requests.get(
            'https://pypi.org/pypi/%s/json' % package.name)
        return resp.json()

    @staticmethod
    def get_code_hosting_repository(project_urls):
        for url in project_urls.values() if project_urls else []:
            matches = re.search(r'github\.com/([\w_-]+/[\w_-]+)', url)
            if matches is not None:
                return matches.group(1)
        return None

    @staticmethod
    def get_code_hosting_topics(code_hosting_repository):
        code_hosting_repository = code_hosting_repository.split('/')
        repository_owner, repository_name = code_hosting_repository
        gql_query = PyPiSource.gql_query % (
            repository_owner, repository_name)
        resp = GithubClient.execute(gql_query)
        return [
            node['topic']['name']
            for node in resp['repository']['topics']['nodes']
        ]

    @staticmethod
    def get_releases(releases, release_regex):
        latest_releases = {}
        for name in releases:
            if releases[name]:
                info = releases[name][0]
                created = parse_datetime(info['upload_time_iso_8601'])
                age = abs(PyPiSource.now - created).days
                if age > PyPiSource.RELEASE_MIN_AGE:
                    continue
                matches = re.search(release_regex, name)
                if matches is not None:
                    prefix = matches.group(2)
                    if prefix in latest_releases:
                        if created < latest_releases[prefix]['created']:
                            continue
                    latest_releases[prefix] = {
                        'name': name,
                        'created': created
                    }
        for release in latest_releases.values():
            yield release
