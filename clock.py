import sys
import subprocess  # nosec
import time

from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler()


@sched.scheduled_job('interval', hours=6)
def watch_releases():
    try:
        start_time = time.time()
        subprocess.run([
            '/usr/bin/python', 'manage.py', 'watch_releases'],
            shell=False)  # nosec
        print('watch_releases finished in %s seconds' % (
            time.time() - start_time))
    except Exception as e:
        print('watch_releases failed %s' % e)


@sched.scheduled_job('interval', hours=6)
def clean_recent_actions():
    try:
        start_time = time.time()
        subprocess.run([
            '/usr/bin/python', 'manage.py', 'clean_recent_actions'],
            shell=False)  # nosec
        print('clean_recent_actions finished in %s seconds' % (
            time.time() - start_time))
    except Exception as e:
        print('clean_recent_actions failed %s' % e)


@sched.scheduled_job('interval', seconds=6)
def clearsessions():
    try:
        start_time = time.time()
        subprocess.run([
            'python', 'manage.py', 'clearsessions'],
            shell=False)  # nosec
        print('clearsessions finished in %s seconds' % (
            time.time() - start_time))
    except Exception as e:
        print('clearsessions failed %s' % e)


@sched.scheduled_job('interval', minutes=15)
def tweet_releases():
    try:
        start_time = time.time()
        subprocess.run([
            '/usr/bin/python', 'manage.py', 'tweet_releases'],
            shell=False)  # nosec
        print('tweet_releases finished in %s seconds' % (
            time.time() - start_time))
    except Exception as e:
        print('tweet_releases failed %s' % e)


try:
    sched.start()
except KeyboardInterrupt:
    sys.exit(0)
