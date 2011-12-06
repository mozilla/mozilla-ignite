from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models.signals import pre_save

from tower import ugettext_lazy as _

from challenges.lib import cached_bleach
from innovate.models import BaseModel, BaseModelManager
from projects.models import Project
from users.models import Profile


class ChallengeManager(BaseModelManager):
    
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Challenge(BaseModel):
    """A user participation challenge on a specific project."""
    
    objects = ChallengeManager()
    
    title = models.CharField(verbose_name=_(u'Title'), max_length=60, unique=True)
    slug = models.SlugField(verbose_name=_(u'Slug'), max_length=60, unique=True)
    summary = models.TextField(verbose_name=_(u'Summary'),
                               validators=[MaxLengthValidator(200)])
    description = models.TextField(verbose_name=_(u'Description'))
    
    def natural_key(self):
        return (self.slug,)
    
    @property
    def description_html(self):
        """Challenge description with bleached HTML."""
        return cached_bleach(self.description)
    
    image = models.ImageField(verbose_name=_(u'Project image'),
                              null=True, blank=True,
                              upload_to=settings.CHALLENGE_IMAGE_PATH)
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
    
    def get_absolute_url(self):
        """Return this challenge's URL.
        
        Note that this needs to account both for an Ignite-style URL structure,
        where there is a single challenge for the entire site, and sites where
        there are multiple challenges.
        
        """
        try:
            # Match for a single-challenge site if we can
            return reverse('challenge_show')
        except NoReverseMatch:
            kwargs = {'project': self.project.slug, 'slug': self.slug}
            return reverse('challenge_show', kwargs=kwargs)


class PhaseManager(BaseModelManager):
    
    def get_from_natural_key(self, challenge_slug, phase_name):
        return self.get(challenge__slug=challenge_slug, name=phase_name)


class Phase(BaseModel):
    """A phase of a challenge."""
    
    objects = PhaseManager()
    
    challenge = models.ForeignKey(Challenge, related_name='phases')
    name = models.CharField(max_length=100)
    
    def natural_key(self):
        return self.challenge.natural_key() +  (self.name,)
    
    natural_key.dependencies = ['challenges.challenge']
    
    # TODO: replace explicit numbering with start and end dates
    order = models.IntegerField()
    
    def __unicode__(self):
        return '%s (%s)' % (self.name, self.challenge.title)
    
    class Meta:
        unique_together = (('challenge', 'name'),)
        ordering = ('order',)


class ExternalLink(BaseModel):
    name = models.CharField(verbose_name=_(u'Link Name'),
        max_length=50)
    url = models.URLField(verbose_name=_(u'URL'),
        max_length=255, verify_exists=False)
    submission = models.ForeignKey('challenges.Submission',
        blank=True, null=True)

    def __unicode__(self):
        return u"%s -> %s" % (self.name, self.url)


class Category(BaseModel):
    name = models.CharField(verbose_name=_(u'Name'), max_length=60, unique=True)
    slug = models.SlugField(verbose_name=_(u'Slug'), max_length=60, unique=True)

    def __unicode__(self):
        return self.name

class Submission(BaseModel):
    """A user's entry into a challenge."""
    
    title = models.CharField(verbose_name=_(u'Title'), max_length=60, unique=True)
    brief_description = models.CharField(max_length=200,
        verbose_name=_(u'Brief Description'),
        help_text = _(u'Think of this as an elevator pitch - keep it short and sweet'))
    description = models.TextField(verbose_name=_(u'Description'))
    sketh_note = models.ImageField(verbose_name=_(u'Featured image'), blank=True, null=True,
        help_text=_(u"This will be used in our summary and list views. You can add more images in your description or link out to sets or images out on the web by adding in an external link"), upload_to=settings.CHALLENGE_IMAGE_PATH)

    @property
    def description_html(self):
        """Challenge description with bleached HTML."""
        return cached_bleach(self.description)
    
    created_by = models.ForeignKey(Profile)
    created_on = models.DateTimeField(
        default=datetime.utcnow()
    )
    
    is_winner = models.BooleanField(verbose_name=_(u'A winning entry?'), default=False)
    """
    The default value for this will be decided depending on it's project
    """
    is_live = models.BooleanField(verbose_name=_(u'Visible to the public?'),
        default=True)
    is_draft = models.BooleanField(verbose_name=_(u'Draft?'),
        help_text=_(u"If you would like some extra time to polish your submission before making it publically then you can set it as draft. When you're ready just un-tick and it will go live"))
    flagged_offensive = models.BooleanField(verbose_name=_(u'Flagged offensive?'), default=False)
    flagged_offensive_reason=models.CharField(verbose_name=_(u'Reason flagged offensive'),
        blank=True, null=True,max_length=100)
    
    phase = models.ForeignKey(Phase)
    
    @property
    def challenge(self):
        return self.phase.challenge
    
    def get_image_src(self):
        media_url = getattr(settings, 'MEDIA_URL', '')
        path = lambda f: f and '%s%s' % (media_url, f)
        return path(self.sketh_note) or path('img/project-default.gif')    
    
    def __unicode__(self):
        return self.title
    
    def _lookup_url(self, view_name, kwargs):
        """Look up a URL related to this submission.
        
        Note that this needs to account both for an Ignite-style URL structure,
        where there is a single challenge for the entire site, and sites where
        there are multiple challenges.
        
        """
        try:
            return reverse(view_name, kwargs=kwargs)
        except NoReverseMatch:
            kwargs.update({'project': self.challenge.project.slug,
                           'slug': self.challenge.slug})
            return reverse(view_name, kwargs=kwargs)
    
    def get_absolute_url(self):
        """Return this submission's URL."""
        return self._lookup_url('entry_show', {'entry_id': self.id})
    
    def get_edit_url(self):
        """Return the URL to edit this submission."""
        return self._lookup_url('entry_edit', {'pk': self.id})
    
    def get_delete_url(self):
        """Return the URL to delete this submission."""
        return self._lookup_url('entry_delete', {'pk': self.id})
    
    def editable_by(self, user):
        """Return True if the user provided can edit this entry."""
        return user.is_superuser or self.owned_by(user)
    
    deletable_by = editable_by
    
    def owned_by(self, user):
        """Return True if user provided owns this entry."""
        return user == self.created_by.user
    
    class Meta:
        ordering = ['-id']


def submission_saved_handler(sender, instance, **kwargs):
    """
    Check if parent participation is set to moderate and set _is_live to False
    """
    if not isinstance(instance, Submission):
        return
    # check submissions we want to moderate don't go direct to live
    instance.is_live = not instance.challenge.moderate


pre_save.connect(submission_saved_handler, sender=Submission)
