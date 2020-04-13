import re

from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


class GithubClient:

    client = None
    access_token = settings.CODE_HOSTINGS['github']['ACCESS_TOKEN']

    @staticmethod
    def get_client():
        if GithubClient.client is None:
            transport = RequestsHTTPTransport(
                url='https://api.github.com/graphql', use_json=True,
                headers={
                    'Authorization': 'bearer %s' % GithubClient.access_token,
                    'Content-type': 'application/json',
                }, verify=True
            )
            GithubClient.client = Client(
                retries=3, transport=transport,
                fetch_schema_from_transport=True
            )
        return GithubClient.client

    @staticmethod
    def execute(gql_query):
        client = GithubClient.get_client()
        resp = client.execute(gql(gql_query))
        return resp


class GithubSource:

    gql_query = '''{
        repository(owner: "%s", name: "%s") {
            description
            homepageUrl
            url
            topics:repositoryTopics(first: 10) {
                nodes {
                  topic {
                    name
                  }
                }
            }
            tags:refs(refPrefix: "refs/tags/", first: 5, orderBy: {
            field: TAG_COMMIT_DATE, direction: DESC}) {
                nodes {
                    name
                    target {
                        ... on Commit {
                            author {
                                date
                            }
                        },
                        ... on Tag {
                            tagger {
                                date
                            }
                        }
                    }
                }
            }
        }
    }'''

    RELEASE_MIN_AGE = 5

    now = timezone.now()

    @staticmethod
    def get_info(package):
        if package.code_hosting_repository:
            info = GithubSource.request(
                *package.code_hosting_repository.split('/'))
            tags = [
                topic['topic']['name'] for topic in info[
                    'topics']['nodes']
            ]
            releases = GithubSource.get_releases(
                info['tags']['nodes'], package.release_regex)
            return {
                'description': info['description'] or '',
                'site_url': info['homepageUrl'] or info['url'],
                'tags': tags, 'releases': releases,
            }
        return None

    @staticmethod
    def request(repository_owner, repository_name):
        gql_query = GithubSource.gql_query % (
            repository_owner, repository_name)
        resp = GithubClient.execute(gql_query)
        return resp['repository']

    @staticmethod
    def get_releases(releases, release_regex):
        prefixes = []
        for release in releases:
            created = parse_datetime(
                release['target']['tagger']['date']
                if 'tagger' in release['target']
                else release['target']['author']['date'])
            age = abs(GithubSource.now - created).days
            if age > GithubSource.RELEASE_MIN_AGE:
                break
            matches = re.search(release_regex, release['name'])
            if matches is not None:
                name = matches.group(1)
                prefix = matches.group(2)
                if prefix in prefixes:
                    continue
                prefixes.append(prefix)
                yield {
                    'name': name.replace('_', '.').replace('-', '.'),
                    'created': created
                }
