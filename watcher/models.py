from django.db import models
from django.utils.translation import gettext_lazy as _

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from model_utils.models import TimeStampedModel
from model_utils import Choices


class Package(TimeStampedModel):
    TECHNOLOGY_CHOICES = Choices(
        ('python', 'python'),
        ('node', 'node'),
    )

    TWITTER_ACCOUNT_CHOICES = Choices(
        ('pypackages', 'pypackages'),
    )

    CODE_HOSTING_CHOICES = Choices(
        ('github', 'github'),
    )

    name = models.CharField(_('name'), max_length=100)
    technology = models.CharField(
        _('technology'), max_length=30, choices=TECHNOLOGY_CHOICES)
    twitter_account = models.CharField(
        _('twitter account'), max_length=30, choices=TWITTER_ACCOUNT_CHOICES)
    code_hosting = models.CharField(
        _('code hosting'), max_length=30, choices=CODE_HOSTING_CHOICES)
    repository = models.CharField(_('repository'), max_length=200)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    class Meta:
        verbose_name = _('package')
        verbose_name_plural = _('packages')
        unique_together = [
            ['name', 'technology'],
            ['code_hosting', 'repository'],
        ]


class Release(TimeStampedModel):
    STATUS_CHOICES = Choices(
        ('new', _('new')),
        ('available', _('available')),
        ('tweeted', _('tweeted')),
        ('fail', _('fail')),
    )

    name = models.CharField(_('name'), max_length=30)
    body = models.TextField(_('body'), blank=True)
    prerelease = models.BooleanField(_('prerelease'))
    published_at = models.DateTimeField(_('published at'))
    status = models.CharField(
        _('status'), max_length=30, db_index=True, choices=STATUS_CHOICES,
        default=STATUS_CHOICES.new)
    package = models.ForeignKey('Package', on_delete=models.CASCADE)

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


class Log(TimeStampedModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    message = models.TextField(_('message'))
