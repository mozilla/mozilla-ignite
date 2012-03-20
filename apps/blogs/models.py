from django.db import models
from django.contrib import admin

from innovate.models import BaseModel

class BlogEntry(BaseModel):
    title = models.CharField(max_length=255)
    link = models.URLField()
    summary = models.TextField(blank=True, null=True)
    page = models.CharField(max_length=50)
    checksum = models.CharField(max_length=32, unique=True)
    updated = models.DateTimeField()
    autor = models.CharField(max_length=255)

    def __unicode__(self):
        return '%s - %s' % (
            self.title, 
            self.page
        )

admin.site.register(BlogEntry)
