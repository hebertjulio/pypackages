import sys
import traceback

from django.core import mail
from django.views.debug import ExceptionReporter


def send_manually_exception_email(subject):
    """ Send e-mail to admins when execption occours. """
    exc_info = sys.exc_info()
    reporter = ExceptionReporter(None, is_email=True, *exc_info)
    message = str(traceback.format_exception(*exc_info))
    mail.mail_admins(
        subject, message, fail_silently=True,
        html_message=reporter.get_traceback_html()
    )
