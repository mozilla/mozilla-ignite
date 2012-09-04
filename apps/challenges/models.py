from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from markdown import markdown

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse, NoReverseMatch
from django.core.validators import MaxLengthValidator
from django.template.defaultfilters import slugify
from django.db import models
from django.db.models import signals
from django.dispatch import receiver

from challenges.lib import cached_bleach, cached_property
from challenges.managers import (SubmissionHelpManager, PhaseManager,
                                 SubmissionManager)
from django_extensions.db.fields import (AutoSlugField,
                                         CreationDateTimeField,
                                         ModificationDateTimeField)
from innovate.models import BaseModel, BaseModelManager
from innovate.utils import ImageStorage
from projects.models import Project
from tower import ugettext_lazy as _
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
                                      default=datetime.utcnow)
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

    def _lookup_url(self, view_name, kwargs=None):
        """Look up a URL related to this challenge.

        Note that this needs to account both for an Ignite-style URL structure,
        where there is a single challenge for the entire site, and sites where
        there are multiple challenges.

        """
        if kwargs is None:
            kwargs = {}
        try:
            return reverse(view_name, kwargs=kwargs)
        except NoReverseMatch:
            kwargs.update({'project': self.project.slug, 'slug': self.slug})
            return reverse(view_name, kwargs=kwargs)

    def get_absolute_url(self):
        """Return this challenge's URL."""
        return self._lookup_url('challenge_show')


def in_six_months():
    return datetime.utcnow() + relativedelta(months=6)


def has_phase_finished(phase):
    """Helper to determine if the ``Ideation`` phase has finished"""
    cache_key = '%s_END_DATE' % phase.upper()
    end_date = cache.get(cache_key)
    if not end_date:
        phase = Phase.objects.get_ideation_phase()
        cache.set(cache_key, end_date)
        if not phase:
            return False
        end_date = phase.end_date
    return datetime.utcnow() > end_date


class Phase(BaseModel):
    """A phase of a challenge."""
    challenge = models.ForeignKey(Challenge, related_name='phases')
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField(verbose_name=_(u'Start date'),
                                      default=datetime.utcnow)
    end_date = models.DateTimeField(verbose_name=_(u'End date'),
                                    default=in_six_months)
    judging_start_date = models.DateTimeField(
        verbose_name=_(u'Judging start date'), blank=True, null=True)
    judging_end_date = models.DateTimeField(
        verbose_name=_(u'Judging end date'), blank=True, null=True)
    order = models.IntegerField()

    # managers
    objects = PhaseManager()

    class Meta:
        unique_together = (('challenge', 'name'),)
        ordering = ('order',)

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.challenge.title)

    def natural_key(self):
        return self.challenge.natural_key() + (self.name,)
    natural_key.dependencies = ['challenges.challenge']

    @models.permalink
    def get_absolute_url(self):
        slug = 'ideas' if self.is_ideation else 'apps'
        return ('entries_all', [slug])

    @cached_property
    def days_remaining(self):
        now = datetime.utcnow()
        if not self.is_open:
            return -1
        time_remaining = self.end_date - now
        return time_remaining.days if time_remaining.days >= 0 else -1

    @cached_property
    def days_until(self):
        now = datetime.utcnow()
        if not self.is_closed:
            return -1
        time_until = self.start_date - now
        return time_until.days if time_until.days >= 0 else -1

    @cached_property
    def phase_rounds(self):
        return self.phaseround_set.all()

    @cached_property
    def current_round(self):
        """Determines the current open ``PhaseRound`` for this ``Phase``"""
        now = datetime.utcnow()
        # we have a phase ``Round`` open
        for item in self.phase_rounds:
            if item.start_date < now and item.end_date > now:
                return item
        return None

    @cached_property
    def next_round(self):
        """Determines the next open ``PhaseRound`` for this ``Phase``"""
        now = datetime.utcnow()
        upcoming_rounds = self.phase_rounds.filter(start_date__gte=now).order_by('start_date')
        if upcoming_rounds:
            return upcoming_rounds[0]
        else:
            return None

    @cached_property
    def current_judging_round(self):
        """Determines what is the current ``PhaseRound`` being judged"""
        now = datetime.utcnow()
        for item in self.phase_rounds:
            if item.judging_start_date and item.judging_end_date \
                and item.judging_start_date < now \
                and item.judging_end_date > now:
                return item
        return None

    @cached_property
    def is_judgable(self):
        """Determines if it is possible to judge this submission"""
        now = datetime.utcnow()
        # Phase is during Judging period
        if self.judging_start_date and self.judging_end_date \
            and self.judging_start_date < now and self.judging_end_date > now:
            return True
        # Round is during judging period
        if self.current_judging_round:
            return True
        return False

    @cached_property
    def is_open(self):
        """Determines if this ``Phase`` is opened for ``Submissions``"""
        now = datetime.utcnow()
        # If the ``Phase`` has any ``phase_rounds`` its status
        # is determined by the ``current_round``
        if self.phase_rounds:
            if self.current_round:
                return True
            return False
        return self.start_date < now and now < self.end_date

    @property
    def is_closed(self):
        return not self.is_open

    @cached_property
    def has_started(self):
        return datetime.utcnow() > self.start_date

    @cached_property
    def is_ideation(self):
        return self.name == settings.IGNITE_IDEATION_NAME

    @cached_property
    def is_development(self):
        return self.name == settings.IGNITE_DEVELOPMENT_NAME

    @cached_property
    def slug_url(self):
        return 'apps' if self.is_development else 'ideas'


@receiver(signals.post_save, sender=Phase)
def phase_update_cache(instance, **kwargs):
    """Updates the ``end_date`` on the cache for this phase"""
    key = '%s_end_date' % slugify(instance.name)
    cache.set(key.upper(), instance.end_date)


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
    title = models.CharField(verbose_name=_(u'Title'), max_length=60)
    brief_description = models.CharField(
        max_length=200, verbose_name=_(u'Brief Description'),
        help_text = _(u"Think of this as an elevator pitch - keep it short"
                      u" and sweet"))
    description = models.TextField(verbose_name=_(u'Description'))
    sketh_note = models.ImageField(
        verbose_name=_(u'Featured image'), blank=True, null=True,
        help_text=_(u"This will be used in our summary and list views. You "
                    u"can add more images in your description or link out to "
                    u"sets or images out on the web by adding in an external link"),
        upload_to=settings.CHALLENGE_IMAGE_PATH,
        storage=ImageStorage())
    category = models.ForeignKey(Category)
    created_by = models.ForeignKey(Profile)
    created_on = models.DateTimeField(default=datetime.utcnow)
    updated_on = ModificationDateTimeField()
    is_winner = models.BooleanField(verbose_name=_(u'A winning entry?'),
                                    default=False,
                                    help_text=_(u'Mark this entry as green lit'))
    is_draft = models.BooleanField(verbose_name=_(u'Draft?'),
        help_text=_(u"If you would like some extra time to polish your submission"
                    u" before making it publically then you can set it as draft. "
                    u"When you're ready just un-tick and it will go live"))
    phase = models.ForeignKey('challenges.Phase')
    phase_round = models.ForeignKey('challenges.PhaseRound',
                                    blank=True, null=True,
                                    on_delete=models.SET_NULL)
    collaborators = models.TextField(blank=True)
    life_improvements = models.TextField(default="",
                                            verbose_name=_(u'How does this improve the lives of people?'))
    take_advantage = models.TextField(blank=True, null=True,
                                        verbose_name=_(u'How does this make the most of the GENI network?'))
    interest_making = models.TextField(blank=True, null=True,
                                        verbose_name=_(u'Are you interested in making this app?'))
    team_members = models.TextField(blank=True, null=True,
                                    verbose_name=_(u'Tell us about your team making this app'))
    # Add Development Phase fields.
    # Make sure they are not required at the Database level.
    # We will make them required at the ``DevelopmentEntryForm`` Level.
    repository_url = models.URLField(max_length=500, verify_exists=False,
                                     blank=True)
    blog_url = models.URLField(max_length=500, verify_exists=False,
                               blank=True)
    required_effort = models.TextField(blank=True, null=True,
                                    verbose_name=_(u'How much effort do you expect this work to take?'))


    # managers
    objects = SubmissionManager()

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return self.title

    @property
    def description_html(self):
        """Challenge description with bleached HTML."""
        return cached_bleach(markdown(self.description))

    @property
    def challenge(self):
        return self.phase.challenge

    def get_image_src(self):
        media_url = getattr(settings, 'MEDIA_URL', '')
        path = lambda f: f and '%s%s' % (media_url, f)
        return path(self.sketh_note) or path('img/project-default.png')
    
    def _lookup_url(self, view_name, kwargs=None):
        """Look up a URL related to this submission.

        Note that this needs to account both for an Ignite-style URL structure,
        where there is a single challenge for the entire site, and sites where
        there are multiple challenges.

        """
        if kwargs is None:
            kwargs = {}
        try:
            return reverse(view_name, kwargs=kwargs)
        except NoReverseMatch:
            kwargs.update({'project': self.challenge.project.slug,
                           'slug': self.challenge.slug})
            return reverse(view_name, kwargs=kwargs)

    @cached_property
    def parent(self):
        parent_list = self.submissionparent_set.all()
        if parent_list:
            return parent_list[0]
        return None

    @cached_property
    def parent_slug(self):
        if self.parent:
            return self.parent.slug
        # Fallback to the versioning list, this query is expensive.
        # Provided for consistency
        version_list = self.submissionversion_set.select_related('parent').all()
        if version_list:
            return version_list[0].parent.slug
        return None

    @cached_property
    def is_idea(self):
        return self.phase.name == settings.IGNITE_IDEATION_NAME

    @cached_property
    def is_proposal(self):
        return self.phase.name == settings.IGNITE_DEVELOPMENT_NAME

    @cached_property
    def phase_slug(self):
        if self.is_idea:
            return 'ideas'
        return 'apps'

    def get_absolute_url(self):
        """Return this submission's URL."""
        return self._lookup_url('entry_show', {'entry_id': self.parent_slug,
                                               'phase': self.phase_slug})

    def get_edit_url(self):
        """Return the URL to edit this submission."""
        return self._lookup_url('entry_edit', {'pk': self.id,
                                               'phase': self.phase_slug})

    def get_delete_url(self):
        """Return the URL to delete this submission."""
        return self._lookup_url('entry_delete', {'pk': self.id,
                                                 'phase': self.phase_slug})

    def get_judging_url(self):
        """Return the URL to judge this submission."""
        return self._lookup_url('entry_judge', {'pk': self.id})

    # Permission shortcuts, for use in templates
    def _permission_check(self, user, permission_name):
        """Check whether a user has a given permission on this object.

        This has to check both the general object and specific object cases,
        because Django doesn't do the intelligent thing here and fall back on
        the general case when a backend doesn't support per-object permissions.

        """
        return any(user.has_perm(permission_name, obj=obj)
                   for obj in [None, self])

    def visible_to(self, user):
        """Return True if the user provided can see this entry."""
        return self._permission_check(user, 'challenges.view_submission')

    def editable_by(self, user):
        """Return True if the user provided can edit this entry."""
        return self._permission_check(user, 'challenges.edit_submission')

    def deletable_by(self, user):
        """Return True if the user provided can delete this entry."""
        return self._permission_check(user, 'challenges.delete_submission')

    def judgeable_by(self, user):
        """Return True if the user provided is allowed to judge this entry."""
        return self._permission_check(user, 'challenges.judge_submission')

    def owned_by(self, user):
        """Return True if user provided owns this entry."""
        return user == self.created_by.user

    @cached_property
    def needs_booking(self):
        """Determines if this entry needs to book a Timeslot.
        - Entry has been gren lit
        - User hasn't booked a timeslot
        """
        return all([self.is_winner, not self.timeslot_set.all()])

    @property
    def is_green_lit(self):
        return self.is_winner

    def get_judge_score(self, profile):
        try:
            judgement = self.judgement_set.filter(judge=profile)[0]
        except IndexError:
            return None
        return judgement.get_score()

    @property
    def score(self):
        """Returns the current score for the Submission"""
        judgements = [j for j in self.judgement_set.all() if j.complete]
        total = sum(j.get_score() for j in judgements)
        if judgements:
            self.average_score = total / len(judgements)
        else:
            self.average_score = 0
        self.judgement_count = len(judgements)
        return self.average_score

class ExclusionFlag(models.Model):
    """Flags to exclude a submission from judging."""

    submission = models.ForeignKey(Submission)

    notes = models.TextField(blank=True)

    def __unicode__(self):
        return unicode(self.submission)


class JudgingCriterion(models.Model):
    """A numeric rating criterion for judging submissions."""

    question = models.CharField(max_length=250, unique=True)
    # changed from 0 to 1 so the values display as 1 to 10 opposed to 0 to 9
    min_value = 1
    max_value = models.IntegerField(default=10)

    phases = models.ManyToManyField(Phase, blank=True,
                                    related_name='judgement_criteria',
                                    through='PhaseCriterion')

    def __unicode__(self):
        return self.question

    def clean(self):
        if self.min_value >= self.max_value:
            raise ValidationError('Invalid value range %d..%d' %
                                  (self.min_value, self.max_value))

    @property
    def range(self):
        """Return the valid range of values for this criterion."""
        return xrange(self.min_value, self.max_value + 1)

    class Meta:

        verbose_name_plural = 'Judging criteria'
        ordering = ('id',)


class PhaseCriterion(models.Model):
    """
    Assignment of judging criteria to individual phases.
    These include a total weight assigned to each criterion. The score from
    each criterion is multiplied up to have this weight as a maximum value.
    """

    phase = models.ForeignKey(Phase)
    criterion = models.ForeignKey(JudgingCriterion)

    # The total weight afforded to this criterion
    weight = models.DecimalField(max_digits=4, decimal_places=2, default=10)

    class Meta:

        unique_together = (('phase', 'criterion'),)
        verbose_name_plural = 'phase criteria'

    def __unicode__(self):
        return ' - '.join(map(unicode, [self.phase, self.criterion]))


class Judgement(models.Model):
    """A judge's rating of a submission."""

    class Incomplete(RuntimeError):
        """Error class when calculating scores on incomplete judgements."""
        def __init__(self, judgement):
            super_init = super(Judgement.Incomplete, self).__init__
            super_init('Judgement is incomplete', judgement)

    submission = models.ForeignKey(Submission)
    judge = models.ForeignKey(Profile)

    # answers comes through in a foreign key from JudgingAnswer
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return ' - '.join([unicode(self.submission), unicode(self.judge)])

    def get_absolute_url(self):
        return self.submission.get_absolute_url()

    @property
    def complete(self):
        """Whether all the criteria in the submission's phase are rated."""
        criteria = JudgingCriterion.objects.filter(judginganswer__judgement=self)
        return all(c in criteria for c in
                   self.submission.phase.judgement_criteria.all())

    def get_score(self):
        total_score = Decimal('0')
        phase_criteria = self.submission.phase.phasecriterion_set.all()
        try:
            for pc in self.submission.phase.phasecriterion_set.all():
                answer = self.answers.get(criterion=pc.criterion)
                weighting_factor = pc.weight / pc.criterion.max_value
                total_score += weighting_factor * answer.rating
        except JudgingAnswer.DoesNotExist:
            raise Judgement.Incomplete(self)
        return total_score

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


class JudgeAssignment(models.Model):
    """An assignment of a specific judge to a submission."""

    submission = models.ForeignKey(Submission)
    judge = models.ForeignKey(Profile)

    created_on = models.DateTimeField(default=datetime.utcnow)

    def __unicode__(self):
        return unicode(self.submission)

    class Meta:
        unique_together = (('submission', 'judge'),)


class PhaseRound(models.Model):
    """Rounds for a given ``Phase``"""
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name')
    phase = models.ForeignKey('challenges.Phase')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    judging_start_date = models.DateTimeField(
        verbose_name=_(u'Judging start date'), blank=True, null=True)
    judging_end_date = models.DateTimeField(
        verbose_name=_(u'Judging end date'), blank=True, null=True)

    def __unicode__(self):
        return u'%s: %s' % (self.phase, self.name)

    @cached_property
    def is_active(self):
        now = datetime.utcnow()
        return all([now > self.start_date, now < self.end_date])

    @cached_property
    def is_open(self):
        return self.is_active

    @cached_property
    def days_remaining(self):
        now = datetime.utcnow()
        if not self.is_open:
            return -1
        time_remaining = self.end_date - now
        return time_remaining.days if time_remaining.days >= 0 else -1


class SubmissionParent(models.Model):
    """Acts as a proxy for the ``Submissions`` so we can keep them versioned
    Slug should never change since it is the main ID for this submission
    through all the process"""
    ACTIVE = 1
    INACTIVE = 2
    REMOVED = 3
    STATUS_CHOICES = (
        (ACTIVE, _('Active')),
        (INACTIVE, _('Inactive')),
        (REMOVED, _('Removed')),
        )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()
    is_featured = models.BooleanField(default=False)
    submission = models.ForeignKey('challenges.Submission')
    status = models.IntegerField(choices=STATUS_CHOICES, default=ACTIVE)

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'Project: %s' % self.name

    def save(self, *args, **kwargs):
        """Set slug and name from the ``Submission``"""
        if not self.slug:
            self.slug = self.submission.id
        if not self.name:
            self.name = self.submission.title
        super(SubmissionParent, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        kwargs = {
            'entry_id': self.slug,
            'phase': self.submission.phase_slug,
            }
        return ('entry_show', [], kwargs)

    def update_version(self, new_submission):
        """Updates the current ``SubmissionParent`` version"""
        if not self.id:
            raise ValueError('You need to save the SubmissionParent before '
                             'updating versions')
        # Archive the current submission
        SubmissionVersion.objects.create(submission=self.submission,
                                         parent=self)
        self.name = new_submission.title
        self.submission = new_submission
        self.save()


class SubmissionVersion(models.Model):
    """Keeps track of the version of a given ``Submission``"""
    submission = models.ForeignKey('challenges.Submission')
    parent = models.ForeignKey('challenges.SubmissionParent')
    created = CreationDateTimeField()

    class Meta:
        unique_together = (('submission', 'parent'),)

    def __unicode__(self):
        return u'Version for %s on %s' % (self.submission, self.created)


class SubmissionHelp(models.Model):
    """Users can ask for help with a given submission"""
    PUBLISHED = 1
    DRAFT = 2
    STATUS_CHOICES = (
        (PUBLISHED, 'Published'),
        (DRAFT, 'Draft'),
        )
    parent = models.OneToOneField('challenges.SubmissionParent')
    created = CreationDateTimeField()
    updated = ModificationDateTimeField()
    notes = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=DRAFT)

    # managers
    objects = SubmissionHelpManager()

    class Meta:
        verbose_name_plural = 'Submission Help'
        ordering = ('-updated',)

    def __unicode__(self):
        return u'Help needed for %s' % self.parent

    @property
    def is_published(self):
        return self.status == self.PUBLISHED
