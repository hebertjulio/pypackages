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

    CODE_HOSTING = Choices(
        ('github', 'github'),
    )

    name = models.CharField(
        _('name'), max_length=100
    )
    programming_language = models.CharField(
        _('programming language'), max_length=50, choices=PROGRAMMING_LANGUAGE
    )
    code_hosting = models.CharField(
        _('code hosting'), max_length=50, choices=CODE_HOSTING
    )
    repository_owner = models.CharField(
        _('repository owner'), max_length=100
    )
    repository_name = models.CharField(
        _('repository name'), max_length=100
    )
    release_regex = models.CharField(
        _('release regex'), max_length=100
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
            ['code_hosting', 'repository_owner', 'repository_name'],
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
