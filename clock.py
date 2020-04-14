import sys
import subprocess  # nosec
import time

from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler()

args = ['python']
try:
    pyenv_path = str(subprocess.check_output([
        '/usr/bin/which', 'pyenv'], shell=False))  # nosec
    args = [*[pyenv_path.strip(), 'which'], *args]
except subprocess.CalledProcessError:
    args = [*['/usr/bin/which'], *args]

python_path = subprocess.check_output(args, shell=False)  # nosec
PYTHON_PATH = python_path.strip()


@sched.scheduled_job('interval', hours=6)
def watch_releases():
    """ Watching for new relases in code hostings. """
    start_time = time.time()
    subprocess.run([
        PYTHON_PATH, 'manage.py', 'watch_releases'],
        shell=False)  # nosec
    print('watch_releases finished in %s seconds' % (
        time.time() - start_time))


@sched.scheduled_job('interval', hours=6)
def clean_recent_actions():
    """ Clear all recent actions. """
    start_time = time.time()
    subprocess.run([
        PYTHON_PATH, 'manage.py', 'clean_recent_actions'],
        shell=False)  # nosec
    print('clean_recent_actions finished in %s seconds' % (
        time.time() - start_time))


@sched.scheduled_job('interval', hours=6)
def clearsessions():
    """ Clear all invalid sessions. """
    start_time = time.time()
    subprocess.run([
        PYTHON_PATH, 'manage.py', 'clearsessions'],
        shell=False)  # nosec
    print('clearsessions finished in %s seconds' % (
        time.time() - start_time))


@sched.scheduled_job('interval', minutes=30)
def tweet_releases():
    """ Tweet one new release by programming language. """
    start_time = time.time()
    subprocess.run([
        PYTHON_PATH, 'manage.py', 'tweet_releases'],
        shell=False)  # nosec
    print('tweet_releases finished in %s seconds' % (
        time.time() - start_time))


try:
    sched.start()
except KeyboardInterrupt:
    sys.exit(0)
