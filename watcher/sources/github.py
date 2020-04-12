import re

from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


class Github:

    query = '''{
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

    RELEASE_MIN_AGE = 15

    client = None
    now = timezone.now()

    def __init__(self):
        access_token = settings.CODE_HOSTINGS['github']['ACCESS_TOKEN']
        transport = RequestsHTTPTransport(
            url='https://api.github.com/graphql',
            use_json=True,
            headers={
                'Authorization': 'bearer %s' % access_token,
                'Content-type': 'application/json',
            },
            verify=True
        )
        Github.client = Client(
            retries=3,
            transport=transport,
            fetch_schema_from_transport=True
        )

    @staticmethod
    def get_info(package):
        info = Github.request(*package.source_id.split('/'))
        hashtags = Github.get_hasttags(
            info['topics']['nodes'], [
                package.programming_language,
                package.name
            ]
        )
        releases = Github.get_releases(
            info['tags']['nodes'],
            package.release_regex
        )
        return {
            'description': info['description'] or '',
            'site_url': info['homepageUrl'] or info['url'],
            'hashtags': hashtags, 'releases': releases,
        }

    @staticmethod
    def request(repository_owner, repository_name):
        query = gql(Github.query % (
            repository_owner, repository_name)
        )
        resp = Github.client.execute(query)
        return resp['repository']

    @staticmethod
    def get_hasttags(topics, extra_topics):
        hashtags = set()
        for topic in topics + extra_topics:
            hashtag = '#' + topic[
                'topic']['name'] if 'topic' in topic else topic
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
        for release in releases:
            created = parse_datetime(
                release['target']['tagger']['date']
                if 'tagger' in release['target']
                else release['target']['author']['date'])
            age = abs(Github.now - created).days
            if age > Github.RELEASE_MIN_AGE:
                break
            matches = re.search(release_regex, release['name'])
            if matches is not None:
                name = matches.group(1)
                prefix = matches.group(2)
                if 0 in prefixes:
                    break
                if prefix in prefixes:
                    continue
                prefixes.append(prefix)
                yield {
                    'name': name.replace('_', '.').replace('-', '.'),
                    'created': created
                }
