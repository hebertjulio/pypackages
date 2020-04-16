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


@sched.scheduled_job('interval', minutes=30)
def get_pypi_updates():
    """Read http://pypi.org/rss/updates.xml to catch new releases"""
    start_time = time.time()
    subprocess.run([
        PYTHON_PATH, 'manage.py', 'getpypiupdates'],
        shell=False)  # nosec
    print('watch_releases finished in %s seconds' % (
        time.time() - start_time))


@sched.scheduled_job('interval', minutes=45)
def get_packages_info():
    """Get info in Libraries.io to update new and outdated packages"""
    start_time = time.time()
    subprocess.run([
        PYTHON_PATH, 'manage.py', 'getpackagesinfo'],
        shell=False)  # nosec
    print('getpackagesinfo finished in %s seconds' % (
        time.time() - start_time))


@sched.scheduled_job('interval', hours=24)
def clear_recent_actions():
    """Clear recent actions history"""
    start_time = time.time()
    subprocess.run([
        PYTHON_PATH, 'manage.py', 'clearrecentactions'],
        shell=False)  # nosec
    print('clearrecentactions finished in %s seconds' % (
        time.time() - start_time))


@sched.scheduled_job('interval', hours=24)
def clear_sessions():
    """Clear all invalid sessions"""
    start_time = time.time()
    subprocess.run([
        PYTHON_PATH, 'manage.py', 'clearsessions'],
        shell=False)  # nosec
    print('clearsessions finished in %s seconds' % (
        time.time() - start_time))


@sched.scheduled_job('interval', minutes=15)
def tweet_releases():
    """Tweet new releases of packages by twitter accounts"""
    start_time = time.time()
    subprocess.run([
        PYTHON_PATH, 'manage.py', 'tweetreleases'],
        shell=False)  # nosec
    print('tweetreleases finished in %s seconds' % (
        time.time() - start_time))


try:
    sched.start()
except KeyboardInterrupt:
    sys.exit(0)
