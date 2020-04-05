import sys
import re
import traceback
import time

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from ...models import Package, Release, Log


REGEX = r'((\d+)(?:[\.\_]\d+)+)$'
RELEASE_MIN_AGE = 10  # days


class GithubInterface(object):
    query = '''{
        repository(owner: "%s", name: "%s") {
            tags:refs(refPrefix: "refs/tags/", first: 3, orderBy: {
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
        self.client = Client(
            retries=3,
            transport=transport,
            fetch_schema_from_transport=True
        )

    def get_releases(self, repository_owner, repository_name):
        query = gql(self.query % (repository_owner, repository_name))
        releases = self.client.execute(query)
        releases = releases['repository']['tags']['nodes']
        previous_prefix = set()
        for release in releases:
            created = parse_datetime(
                release['target']['author']['date']
                if 'author' in release['target']
                else release['target']['tagger']['date']
            )
            if abs(self.now - created).days <= RELEASE_MIN_AGE:
                matches = re.search(REGEX, release['name'])
                if matches is not None:
                    current_prefix = matches.group(2)
                    name = matches.group(1)
                    if current_prefix not in previous_prefix:
                        previous_prefix.add(current_prefix)
                        yield {
                            'name': name.replace('_', '.'),
                            'created': created
                        }


class Command(BaseCommand):
    help = 'Watch for new releases in code hosting.'

    def handle(self, *args, **options):
        try:
            start_time = time.time()
            code_hostings = {
                'github': GithubInterface(),
            }
            self.processing(code_hostings)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception:
            Log.objects.create(message=traceback.format_exc())
        finally:
            print("watch_releases: %s seconds" % (
                time.time() - start_time))

    def processing(self, code_hostings):
        packages = Package.objects.all()
        for package in packages:
            code_hosting = code_hostings[package.code_hosting]
            releases = code_hosting.get_releases(
                package.repository_owner, package.repository_name)
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

    def add_log(self, message):
        Log.objects.create(message=message)
