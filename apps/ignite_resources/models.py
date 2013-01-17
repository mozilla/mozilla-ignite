from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django_extensions.db.fields import (CreationDateTimeField,
                                         ModificationDateTimeField)


class Resource(models.Model):
    """List of resources"""
    EXTERNAL = 1
    LEARNING = 2
    RESOURCE_CHOICES = (
        (EXTERNAL, _('External Link')),
        (LEARNING, _('Learning Lab')),
        )
    PUBLISHED = 1
    HIDDEN = 2
    STATUS_CHOICES = (
        (PUBLISHED, _('Published')),
        (HIDDEN, _('Hidden')),
        )
    title = models.CharField(max_length=255)
    slug = models.SlugField(verbose_name=_(u'Slug'), max_length=80, unique=True)
    resource_type = models.IntegerField(choices=RESOURCE_CHOICES)
    body = models.TextField()
    url = models.URLField(verify_exists=False, max_length=500, blank=True)
    email = models.EmailField(max_length=150, blank=True)
    is_featured = models.BooleanField(default=False)
    thumbnail = models.ImageField(verbose_name=_(u'Learning Lab thumbnail'),
            null=True, blank=True,
            upload_to=settings.CHALLENGE_IMAGE_PATH)
    status = models.IntegerField(choices=STATUS_CHOICES, default=PUBLISHED)
    template = models.CharField(max_length=255, null=True, blank=True)
    created = CreationDateTimeField()
    updated = ModificationDateTimeField()

    def get_image_src(self):
        media_url = getattr(settings, 'MEDIA_URL', '')
        path = lambda f: f and '%s%s' % (media_url, f)
        return path(self.thumbnail)

    def __unicode__(self):
        return self.title
