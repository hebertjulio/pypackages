from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils.models import TimeStampedModel


class Project(TimeStampedModel):

    name = models.CharField(_('name'), max_length=100, unique=True)
    release = models.CharField(_('release'), max_length=50, default='')
    download_count = models.IntegerField(_('download count'), default=0)
    favorite_count = models.IntegerField(_('favorite count'), default=0)
    retweet_count = models.IntegerField(_('retweet count'), default=0)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        ordering = ['name']
