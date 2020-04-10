import sys
import re

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from ...models import Package, Release


RELEASE_MIN_AGE = 15  # days


class GithubInterface(object):
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
        self.client = Client(
            retries=3,
            transport=transport,
            fetch_schema_from_transport=True
        )
        self.trans = str.maketrans('_-', '..')
        self.now = timezone.now()

    def load_repository(self, repository_owner, repository_name):
        repository_owner = repository_owner.strip()
        repository_name = repository_name.strip()

        query = gql(self.query % (repository_owner, repository_name))
        payload = self.client.execute(query)

        self.repository = payload['repository']
        self.topics = payload['repository']['topics']['nodes']
        self.releases = payload['repository']['tags']['nodes']

    def get_repository(self):
        return {
            'description': self.repository['description'] or '',
            'site_url': self.repository[
                'homepageUrl'] or self.repository['url']
        }

    def get_topics(self):
        for topic in self.topics:
            yield topic['topic']['name']

    def get_releases(self, release_regex):
        release_regex = release_regex.strip()
        previous_prefix = set()

        for release in self.releases:
            created = parse_datetime(
                release['target']['author']['date']
                if 'author' in release['target']
                else release['target']['tagger']['date']
            )
            if abs(self.now - created).days <= RELEASE_MIN_AGE:
                matches = re.search(release_regex, release['name'])
                if matches is not None:
                    current_prefix = matches.group(2)
                    name = matches.group(1)
                    if current_prefix not in previous_prefix:
                        previous_prefix.add(current_prefix)
                        yield {
                            'name': name.translate(self.trans),
                            'created': created
                        }


class Command(BaseCommand):
    help = 'Watch for new releases in code hosting.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        characters = '@/_-#$%*!()&=+[]:;? '
        self.trans = str.maketrans(
            dict(zip(list(characters), [
                '' for v in range(len(characters))])))

    def handle(self, *args, **options):
        try:
            code_hostings = {
                'github': GithubInterface(),
            }
            self.processing(code_hostings)
        except KeyboardInterrupt:
            sys.exit(0)

    def processing(self, code_hostings):
        packages = Package.objects.all()
        for package in packages:
            code_hosting = code_hostings[package.code_hosting]
            code_hosting.load_repository(
                package.repository_owner,
                package.repository_name,
            )

            repository = code_hosting.get_repository()
            topics = code_hosting.get_topics()
            releases = code_hosting.get_releases(package.release_regex)

            hashtags = ' '.join(['#%s' % topic for topic in set([
                topic.translate(self.trans)
                for topic in topics
            ] + [
                package.programming_language,
                package.name.translate(self.trans)
            ])])

            package.description = re.sub(
                r':\w+:', '', repository['description']).encode(
                    'ascii', 'ignore').decode('ascii').strip()

            package.site_url = repository['site_url']

            while True:
                if len(package.description) < 255:
                    break
                package.description = package.description.split(' ')
                package.description = '%s...' % (
                    ' '.join(package.description[:-1]))

            package.hashtags = hashtags
            package.save()

            self.add_release(releases, package)

    def add_release(self, releases, package):
        for release in releases:
            release_exists = Release.objects.filter(
                name=release['name'], package=package
            ).exists()
            if release_exists is False:
                Release.objects.create(**{
                    **release, 'package': package
                })
