from datetime import datetime
from dateutil.relativedelta import relativedelta
from markdown import markdown

from django.conf import settings
from django.core.exceptions import ValidationError
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

    def get_current_phase(self, slug):
        now = datetime.now()
        return self.filter(
            challenge__slug=slug
        ).filter(
            start_date__lte=now
        ).filter(
            end_date__gte=now
        )


class Phase(BaseModel):
    """A phase of a challenge."""
    
    objects = PhaseManager()
    
    challenge = models.ForeignKey(Challenge, related_name='phases')
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField(verbose_name=_(u'Start date'),
                                      default=datetime.now())
    end_date = models.DateTimeField(verbose_name=_(u'End date'),
                                        default=datetime.now() + relativedelta( months = +6 ))

    
    def natural_key(self):
        return self.challenge.natural_key() +  (self.name,)
    
    natural_key.dependencies = ['challenges.challenge']
    
    order = models.IntegerField()
    
    def days_remaining(self):
        return self.end_date - datetime.now()
    
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

class CategoryManager(BaseModelManager):
    
    def get_active_categories(self):
        
        filtered_cats = []
        for cat in Category.objects.all():
            cat_submissions = cat.submission_set.all()
            if cat_submissions.count():
                filtered_cats.append(cat)

        if len(filtered_cats) == 0:
            return False
        else:
            return filtered_cats


class Category(BaseModel):
    
    objects = CategoryManager()
    
    name = models.CharField(verbose_name=_(u'Name'), max_length=60, unique=True)
    slug = models.SlugField(verbose_name=_(u'Slug'), max_length=60, unique=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        
        verbose_name_plural = 'Categories'


class Submission(BaseModel):
    """A user's entry into a challenge."""
    
    title = models.CharField(verbose_name=_(u'Title'), max_length=60, unique=True)
    brief_description = models.CharField(max_length=200,
        verbose_name=_(u'Brief Description'),
        help_text = _(u'Think of this as an elevator pitch - keep it short and sweet'))
    description = models.TextField(verbose_name=_(u'Description'))
    sketh_note = models.ImageField(verbose_name=_(u'Featured image'), blank=True, null=True,
        help_text=_(u"This will be used in our summary and list views. You can add more images in your description or link out to sets or images out on the web by adding in an external link"), upload_to=settings.CHALLENGE_IMAGE_PATH)
    
    category = models.ForeignKey(Category)

    @property
    def description_html(self):
        """Challenge description with bleached HTML."""
        return cached_bleach(markdown(self.description))
    
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
    
    def get_judging_url(self):
        """Return the URL to judge this submission."""
        return self._lookup_url('entry_judge', {'pk': self.id})
    
    # Permission shortcuts, for use in templates
    
    def editable_by(self, user):
        """Return True if the user provided can edit this entry."""
        return user.has_perm('challenges.edit_submission', obj=self)
    
    def deletable_by(self, user):
        """Return True if the user provided can delete this entry."""
        return user.has_perm('challenges.delete_submission', obj=self)
    
    def judgeable_by(self, user):
        """Return True if the user provided is allowed to judge this entry."""
        return user.has_perm('challenges.judge_submission', obj=self)
    
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


class JudgingCriterion(models.Model):
    """A numeric rating criterion for judging submissions."""
    
    question = models.CharField(max_length=250, unique=True)
    min_value = models.IntegerField(default=0)
    max_value = models.IntegerField(default=10)
    
    phases = models.ManyToManyField(Phase, blank=True,
                                    related_name='judgement_criteria')
    
    def __unicode__(self):
        return self.question
    
    def clean(self):
        if self.min_value > self.max_value:
            raise ValidationError('Invalid value range %d..%d' %
                                  (self.min_value, self.max_value))
    
    @property
    def range(self):
        """Return the valid range of values for this criterion."""
        return xrange(self.min_value, self.max_value + 1)
    
    class Meta:
        
        verbose_name_plural = 'Judging criteria'
        ordering = ('id',)


class Judgement(models.Model):
    """A judge's rating of a submission."""
    
    submission = models.ForeignKey(Submission)
    judge = models.ForeignKey(Profile)
    
    # answers comes through in a foreign key from JudgingAnswer
    notes = models.TextField(blank=True)
    
    def __unicode__(self):
        return ' - '.join([unicode(self.submission), unicode(self.judge)])
    
    def get_absolute_url(self):
        return self.submission.get_absolute_url()
    
    class Meta:
        unique_together = (('submission', 'judge'),)


class JudgingAnswer(models.Model):
    """A judge's answer to an individual judging criterion."""
    
    judgement = models.ForeignKey(Judgement, related_name='answers')
    criterion = models.ForeignKey(JudgingCriterion)
    rating = models.IntegerField()
    
    def __unicode__(self):
        return ' - '.join([unicode(self.judgement), unicode(self.criterion)])
    
    class Meta:
        unique_together = (('judgement', 'criterion'),)
    
    def clean(self):
        criterion = self.criterion
        if self.rating not in self.criterion.range:
            raise ValidationError('Rating %d is outside the range %d to %d' %
                                  (self.rating, self.criterion.min_value,
                                   self.criterion.max_value))
