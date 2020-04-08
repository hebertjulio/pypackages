import sys
import subprocess
import time

from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler()


@sched.scheduled_job('interval', hours=6)
def watch_releases():
    try:
        start_time = time.time()
        subprocess.check_output(['python', 'manage.py', 'watch_releases'])
        print('watch_releases finished in %s seconds' % (
            time.time() - start_time))
    except Exception as e:
        print('watch_releases failed %s' % e)


@sched.scheduled_job('interval', hours=24)
def clean_recent_actions():
    try:
        start_time = time.time()
        subprocess.check_output(
            ['python', 'manage.py', 'clean_recent_actions'])
        print('clean_recent_actions finished in %s seconds' % (
            time.time() - start_time))
    except Exception as e:
        print('clean_recent_actions failed %s' % e)


@sched.scheduled_job('interval', hours=24)
def clearsessions():
    try:
        start_time = time.time()
        subprocess.check_output(['python', 'manage.py', 'clearsessions'])
        print('clearsessions finished in %s seconds' % (
            time.time() - start_time))
    except Exception as e:
        print('clearsessions failed %s' % e)


@sched.scheduled_job('interval', minutes=30)
def tweet_releases():
    try:
        start_time = time.time()
        subprocess.check_output([
            'python', 'manage.py', 'tweet_releases'])
        print('tweet_releases finished in %s seconds' % (
            time.time() - start_time))
    except Exception as e:
        print('tweet_releases failed %s' % e)


try:
    sched.start()
except KeyboardInterrupt:
    sys.exit(0)
