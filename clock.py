import sys
import subprocess
import time

from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler()


@sched.scheduled_job('interval', hours=4)
def watch_releases():
    try:
        print('watch_releases: starting')
        start_time = time.time()
        subprocess.check_output(['python', 'manage.py', 'watch_releases'])
        print('watch_releases: finished in %s seconds' % (
            time.time() - start_time))
    except Exception:
        print('watch_releases: failed')


@sched.scheduled_job('interval', hours=1)
def clean_recent_actions():
    try:
        print('clean_recent_actions: starting')
        start_time = time.time()
        subprocess.check_output(
            ['python', 'manage.py', 'clean_recent_actions'])
        print('clean_recent_actions: finished in %s seconds' % (
            time.time() - start_time))
    except Exception:
        print('clean_recent_actions: failed')


@sched.scheduled_job('interval', hours=1)
def clearsessions():
    try:
        print('clearsessions: starting')
        start_time = time.time()
        subprocess.check_output(['python', 'manage.py', 'clearsessions'])
        print('clearsessions: finished in %s seconds' % (
            time.time() - start_time))
    except Exception:
        print('clearsessions: failed')


@sched.scheduled_job('interval', minutes=30)
def tweet_releases():
    try:
        print('tweet_releases: starting')
        start_time = time.time()
        subprocess.check_output([
            'python', 'manage.py', 'tweet_releases'])
        print('tweet_releases: finished in %s seconds' % (
            time.time() - start_time))
    except Exception:
        print('tweet_releases: failed')


try:
    sched.start()
except KeyboardInterrupt:
    sys.exit(0)
