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

    SOURCE = Choices(
        ('github', 'github'),
        ('pypi', 'pypi'),
    )

    name = models.CharField(
        _('name'), max_length=100
    )
    programming_language = models.CharField(
        _('programming language'), max_length=50, choices=PROGRAMMING_LANGUAGE
    )
    source = models.CharField(
        _('source'), max_length=50, choices=SOURCE
    )
    code_hosting_repository = models.CharField(
        _('code hosting repository'), max_length=200,
        blank=True, help_text=_('repository owner/name')
    )
    release_regex = models.CharField(
        _('release regex'), max_length=100,
        help_text=_('^v?((\\d+)(?:\\.\\d+)+)$'),
    )
    tags = models.CharField(
        _('tags'), max_length=255, blank=True
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
