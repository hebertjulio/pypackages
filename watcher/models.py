from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils.models import TimeStampedModel
from model_utils import Choices


class Package(TimeStampedModel):
    PROGRAMMING_LANGUAGE = Choices(
        ('python', 'python'),
    )

    STATUS = Choices(
        ('new', _('new')),
        ('done', _('done')),
        ('fail', _('fail')),
    )

    name = models.CharField(_('name'), max_length=100)
    programming_language = models.CharField(
        _('programming language'), max_length=50,
        choices=PROGRAMMING_LANGUAGE
    )
    rank = models.PositiveIntegerField(_('rank'), db_index=True, default=0)
    repository = models.CharField(_('repository'), max_length=200, blank=True)
    keywords = models.CharField(_('keywords'), max_length=255)
    description = models.CharField(_('description'), max_length=255)
    homepage = models.CharField(_('homepage'), max_length=255)
    stable_regex = models.CharField(
        _('stable regex'), max_length=100, blank=True)
    status = models.CharField(
        _('status'), max_length=50, db_index=True,
        default=STATUS.new, choices=STATUS
    )
    message = models.TextField(_('message'), blank=True)
    last_release = models.CharField(_('last release'), max_length=50)
    has_new_release = models.BooleanField(_('has new release'))

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    class Meta:
        verbose_name = _('package')
        verbose_name_plural = _('packages')
        unique_together = [
            ['name', 'programming_language'],
        ]
        ordering = ['name']
