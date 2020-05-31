from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils.models import TimeStampedModel
from model_utils import Choices


class Project(TimeStampedModel):

    STATUS = Choices(
        ('new', _('new')),
        ('waiting', _('waiting')),
        ('done', _('done')),
        ('fail', _('fail')),
    )

    name = models.CharField(_('name'), max_length=100, unique=True)
    release = models.CharField(_('release'), max_length=50, default='')
    downloads = models.IntegerField(_('downloads'), default=0)

    status = models.CharField(
        _('status'), max_length=50, db_index=True,
        default=STATUS.new, choices=STATUS
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        ordering = ['name']
