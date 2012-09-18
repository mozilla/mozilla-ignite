from django.contrib import admin
from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import (AutoSlugField, CreationDateTimeField,
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
    slug = AutoSlugField(populate_from='title')
    resource_type = models.IntegerField(choices=RESOURCE_CHOICES)
    body = models.TextField()
    url = models.URLField(verify_exists=False, max_length=500, blank=True)
    email = models.EmailField(max_length=150, blank=True)
    is_featured = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=PUBLISHED)
    template = models.CharField(max_length=255, null=True, blank=True)
    created = CreationDateTimeField()
    updated = ModificationDateTimeField()

    def __unicode__(self):
        return self.title


admin.site.register(Resource)
