from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils.models import TimeStampedModel
from model_utils import Choices


class Package(TimeStampedModel):
    PROGRAMMING_LANGUAGE = Choices(
        ('python', 'python'),
        ('javascript', 'javascript'),
        ('css', 'css'),
    )

    SOURCE_TYPE = Choices(
        ('github', 'github'),
        ('pypi', 'pypi'),
    )

    name = models.CharField(
        _('name'), max_length=100
    )
    programming_language = models.CharField(
        _('programming language'), max_length=50, choices=PROGRAMMING_LANGUAGE
    )
    source_type = models.CharField(
        _('source type'), max_length=50, choices=SOURCE_TYPE
    )
    source_id = models.CharField(
        _('source id'), max_length=200,
        help_text=_((
            'Repository owner/name of Github, or '
            'package name if PyPi'))
    )
    release_regex = models.CharField(
        _('release regex'), max_length=100,
        help_text=_('Ex. ^v?((\\d+)(?:\\.\\d+)+)$'),
    )
    hashtags = models.CharField(
        _('hashtags'), max_length=255, blank=True
    )
    description = models.CharField(
        _('description'), max_length=255, blank=True
    )
    site_url = models.CharField(
        _('site url'), max_length=255, blank=True
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    class Meta:
        verbose_name = _('package')
        verbose_name_plural = _('packages')
        unique_together = [
            ['name', 'programming_language'],
            ['source_type', 'source_id'],
        ]
        ordering = [
            'name',
        ]


class Release(TimeStampedModel):
    STATUS = Choices(
        ('new', _('new')),
        ('tweeted', _('tweeted')),
    )

    name = models.CharField(
        _('name'), max_length=50
    )
    status = models.CharField(
        _('status'), max_length=50, db_index=True,
        choices=STATUS, default=STATUS.new
    )
    package = models.ForeignKey(
        'Package', on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    class Meta:
        verbose_name = _('release')
        verbose_name_plural = _('releases')
        unique_together = [
            ['name', 'package'],
        ]
        ordering = [
            '-created',
        ]
