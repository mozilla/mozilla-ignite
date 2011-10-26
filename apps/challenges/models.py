from datetime import datetime

from django.conf import settings
from django.db import models
from django.core.validators import MaxLengthValidator

from tower import ugettext_lazy as _

from innovate.models import BaseModel
from projects.models import Project


class Challenge(BaseModel):
    """A user participation challenge on a specific project."""
    
    title = models.CharField(verbose_name=_(u'Title'), max_length=60, unique=True)
    slug = models.SlugField(verbose_name=_(u'Slug'), max_length=60, unique=True)
    summary = models.TextField(verbose_name=_(u'Summary'),
                               validators=[MaxLengthValidator(200)])
    description = models.TextField(verbose_name=_(u'Description'))
    description_html = models.TextField(verbose_name=_(u'Description with bleached HTML'),
                                        null=True,
                                        blank=True)
    image = models.ImageField(verbose_name=_(u'Project image'),
                              null=True, blank=True,
                              upload_to=settings.PARTICIPATION_IMAGE_PATH)
    start_date = models.DateTimeField(verbose_name=_(u'Start date'),
                                      default=datetime.now)
    end_date = models.DateTimeField(verbose_name=_(u'End date'))
    moderate = models.BooleanField(verbose_name=_(u'Moderate entries'),
                                   default=False)
    allow_voting = models.BooleanField(verbose_name=_(u'Can users vote on submissions?'),
                                       default=False)
    project = models.ForeignKey(Project, verbose_name=_(u'Project'),
                                limit_choices_to={'allow_participation': True})

    def get_image_src(self):
        media_url = getattr(settings, 'MEDIA_URL', '')
        path = lambda f: f and '%s%s' % (media_url, f)
        return path(self.image) or path('img/project-default.gif')

    def __unicode__(self):
        return self.title
