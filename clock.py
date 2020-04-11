import sys
import subprocess  # nosec
import time

from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler()


@sched.scheduled_job('interval', hours=12)
def watch_releases():
    start_time = time.time()
    subprocess.run([
        'python', 'manage.py', 'watch_releases'],
        shell=False)  # nosec
    print('watch_releases finished in %s seconds' % (
        time.time() - start_time))


@sched.scheduled_job('interval', hours=12)
def clean_recent_actions():
    start_time = time.time()
    subprocess.run([
        'python', 'manage.py', 'clean_recent_actions'],
        shell=False)  # nosec
    print('clean_recent_actions finished in %s seconds' % (
        time.time() - start_time))


@sched.scheduled_job('interval', hours=12)
def clearsessions():
    start_time = time.time()
    subprocess.run([
        'python', 'manage.py', 'clearsessions'],
        shell=False)  # nosec
    print('clearsessions finished in %s seconds' % (
        time.time() - start_time))


@sched.scheduled_job('interval', minutes=30)
def tweet_releases():
    start_time = time.time()
    subprocess.run([
        'python', 'manage.py', 'tweet_releases'],
        shell=False)  # nosec
    print('tweet_releases finished in %s seconds' % (
        time.time() - start_time))


try:
    sched.start()
except KeyboardInterrupt:
    sys.exit(0)
