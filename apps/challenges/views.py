import itertools
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.list import ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import ProcessFormView, DeleteView, ModelFormMixin

import jingo
from tower import ugettext as _
from awards.forms import AwardForm
from awards.models import JudgeAllowance
from voting.models import Vote
from badges.models import SubmissionBadge
from commons.helpers import get_page, get_paginator
from challenges.decorators import (phase_open_required, phase_closed_required,
                                   project_challenge_required, judge_required)
from challenges.forms import (EntryForm, EntryLinkForm, InlineLinkFormSet,
                              JudgingForm, NewEntryForm, SubmissionHelpForm,
                              SubmissionHelp, DevelopmentEntryForm,
                              NewDevelopmentEntryForm, BaseExternalLinkFormSet)
from challenges.models import (Challenge, Phase, Submission, Category,
                               ExternalLink, Judgement, SubmissionParent,
                               JudgeAssignment, SubmissionVersion)
from projects.models import Project
from timeslot.models import TimeSlot


LOGGER = logging.getLogger(__name__)


def get_phase_or_404(slug):
    """Returns the appropriate ``Phase`` to the given slug
    ``ideas`` or ``proposals`` or raise ``Http404``"""
    phase = None
    if slug == 'ideas':
        phase = Phase.objects.get_ideation_phase()
    if slug == 'proposals':
        phase = Phase.objects.get_development_phase()
    if phase:
        return phase
    raise Http404


class JingoTemplateMixin(TemplateResponseMixin):
    """View mixin to render through Jingo rather than Django's renderer."""

    def render_to_response(self, context, **response_kwargs):
        """Render using Jingo and return the response."""
        template_names = self.get_template_names()
        if len(template_names) > 1:
            LOGGER.info('Jingo only works with a single template name; '
                        'discarding ' + ', '.join(template_names[1:]))
        template_name = template_names[0]

        return jingo.render(self.request, template_name, context,
                            **response_kwargs)


def get_list_count(*args):
    """Calculates the number of elements in the list of lists passed"""
    return len(list(itertools.chain(*args)))


def show(request, project, slug, phase, template_name='challenges/show.html',
         category=False):
    """Show an individual project challenge."""
    try:
        challenge = (Challenge.objects.select_related('project')
                     .get(project__slug=project, slug=slug))
    except Challenge.DoesNotExist:
        raise Http404
    project = challenge.project
    """Pagination options """
    # TODO
    entry_set = Submission.objects.visible(request.user)
    entry_set = entry_set.filter(phase__challenge=challenge, phase=phase)
    if category:
        entry_set = entry_set.filter(category__name=category)
    page_number = get_page(request.GET)
    entries = get_paginator(entry_set, page_number, 6)
    try:
        category = Category.objects.get(slug=category)
    except ObjectDoesNotExist:
        category = False
    # 'days_remaining': request.phase['days_remaining']
    days_remaning = request.ideation.days_remaining
    return jingo.render(request, template_name, {
        'challenge': challenge,
        'project': project,
        'phases': list(enumerate(challenge.phases.all(), start=1)),
        'entries': entries,
        'categories': Category.objects.get_active_categories(),
        'category': category,
        'days_remaining': days_remaning,
        'phase': phase,
    })


def entries_all(request, project, slug, phase):
    """Show all entries (submissions) to a challenge."""
    phase = get_phase_or_404(phase)
    return show(request, project, slug, phase, template_name='challenges/all.html')


@project_challenge_required
def entries_winning(request, project, challenge):
    """Show entries that have been marked as winners and awarded."""
    submissions = (Submission.objects.visible(request.user)
                   .filter(phase__challenge=challenge)
                   .filter(is_winner=True)
                   .order_by('phase', 'phase_round'))
    context = {
        'entries': submissions,
        'project': project,
        'challenge': challenge,
        }
    return jingo.render(request, 'challenges/winning.html', context)


@login_required
@judge_required
@project_challenge_required
def entries_assigned(request, project, challenge):
    """Show entries assigned to be judged and awarded by the current user.
    In order to award green-lited submissions
    - Judge has allowance
    - The Award money has been released
    """
    profile = request.user.get_profile()
    # Submissions assigned to the user
    submissions = (Submission.objects
                   .assigned_to_user(profile)
                   # excluding this will return only non judged submissions
                   # .exclude(judgement__judge=profile)
                   .order_by('phase', 'phase_round'))
    for submission in submissions:
        submission.has_judged = any(j.judge.user == request.user
                                    for j in submission.judgement_set.all())
    context = {
        'project': project,
        'challenge': challenge,
        'entries': sorted(submissions, key=lambda s: s.has_judged,
                          reverse=True),
        }
    # Award context
    allowance = JudgeAllowance.objects.get_for_judge(profile)
    if allowance:
        context['allowance'] = allowance
        context['awarded_list'] = (allowance.submissionaward_set
                                   .filter(judge_allowance__judge=profile))
        awarded_ids = [o.submission.id for o in context['awarded_list']]
        context['greenlit_list'] = (Submission.objects
                                    .green_lit(allowance.award.phase,
                                               allowance.award.phase_round)
                                    .filter(~Q(id__in=awarded_ids)))
    return jingo.render(request, 'challenges/assigned.html', context)


@login_required
@judge_required
@project_challenge_required
def entries_judged(request, project, challenge):
    submissions = (Submission.objects
                   .select_related('judgement__judginganswer__criterion')
                   .filter(judgement__isnull=False).distinct())
    for submission in submissions:
        judgements = [j for j in submission.judgement_set.all() if j.complete]
        total = sum(j.get_score() for j in judgements)
        if judgements:
            submission.average_score = total / len(judgements)
        else:
            submission.average_score = 0
        submission.judgement_count = len(judgements)
    submissions = sorted(submissions, key=lambda s: s.average_score,
                         reverse=True)
    context = {
        'project': project,
        'challenge': challenge,
        'entries': submissions,
        }
    return jingo.render(request, 'challenges/judged.html', context)


def entries_category(request, project, slug, category, phase):
    """Show all entries to a specific category"""
    phase = get_phase_or_404(phase)
    return show(request, project, slug, phase,
                template_name='challenges/all.html', category=category)

LinkFormSet = formset_factory(EntryLinkForm, extra=2,
                                  formset=BaseExternalLinkFormSet)


def get_submissionparent_or_404(challenge, **kwargs):
    try:
        return (SubmissionParent.objects.select_related('submission')
                .get(submission__phase__challenge=challenge, **kwargs))
    except SubmissionParent.DoesNotExist:
        raise Http404


def add_submission(request, phase, form_class=NewEntryForm,
                   template='challenges/create.html', extra_context=None):
    """Adds a ``Submission`` to the selected ``Phase``"""
    error_count = 0
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        link_form = LinkFormSet(request.POST, prefix="externals")
        if form.is_valid() and link_form.is_valid():
            # prepare fields to be saved
            entry = form.save(commit=False)
            entry.created_by = request.user.get_profile()
            entry.phase = phase
            if phase.current_round:
                entry.phase_round = phase.current_round
            entry.save()
            for link in link_form.cleaned_data:
                if all(i in link for i in ("name", "url")):
                    ExternalLink.objects.create(name=link['name'],
                                                url=link['url'],
                                                submission=entry)
            SubmissionParent.objects.create(submission=entry)
            if entry.is_draft:
                msg = _('<strong>Your entry has been saved as draft.</strong>'
                        ' When you want the world to see it then uncheck the '
                        '"Save as draft?" option from your idea editting page')
            else:
                msg = _('Your entry has been posted successfully and is now '
                        'available for public review')
            messages.success(request, msg)
            return HttpResponseRedirect(phase.get_absolute_url())
        error_count = get_list_count(form.errors, link_form.non_form_errors())
    else:
        form = form_class()
        link_form = LinkFormSet(prefix='externals')
    context = {
        'form': form,
        'link_form': link_form,
        'error_count': error_count,
        'phase': phase,
        }
    if extra_context:
        context.update(extra_context)
    return jingo.render(request, template, context)


@login_required
@project_challenge_required
def create_entry(request, project, challenge, phase):
    """Creates a Ideation ``Submission`` with the details provided.
    Once the phase is closed we 404.
    """
    phase = get_phase_or_404(phase)
    form_class = NewEntryForm if phase.is_ideation else NewDevelopmentEntryForm
    # Phase must be open
    if not phase or not phase.is_open:
        raise Http404
    extra_context = {
        'project': project,
        'challenge': challenge,
        }
    return add_submission(request, phase, form_class=form_class,
                          extra_context=extra_context)


@project_challenge_required
def entry_version(request, project, challenge, entry_id):
    """Redirects an ``Submission`` version to the ``SubmissionParent``"""
    try:
        parent = (SubmissionParent.objects.select_related('submission')
                  .get(submission__id=entry_id,
                       submission__phase__challenge=challenge))
        return HttpResponseRedirect(parent.get_absolute_url())
    except SubmissionParent.DoesNotExist:
        pass
    # Submission was versioned and has a new SubmissionParent
    try:
        version = (SubmissionVersion.objects.select_related('submission_list')
                   .filter(submission__id=entry_id,
                           submission__phase__challenge=challenge))[0]
    except IndexError:
        raise Http404
    return HttpResponseRedirect(version.parent.get_absolute_url())


def get_award_context(submission, user):
    """Context for the judge released allocated ``Award`` for ``Submission``"""
    if not user.is_judge:
        return {}
    profile = user.get_profile()
    # Does judge have a ``RELEASED`` allowance
    allowance = JudgeAllowance.objects.get_for_judge(profile)
    if not allowance:
        return {}
    try:
        award = (allowance.submissionaward_set
                 .filter(submission=submission,
                         judge_allowance__judge=profile))[0]
        award_form = AwardForm({'amount': award.amount})
    except IndexError:
        award = None
        award_form = None
    # Hasn't awarded this submission but has allowance for this Round/Phase
    # and the submission has been green ilt
    if not award and allowance.is_same_round(submission) \
        and submission.is_green_lit:
        award_form = AwardForm()
    return {
        'allowance': allowance,
        'award_form': award_form,
        'award': award,
        }


def get_judging_context(user, submission, judging_form=None):
    """Context for the Judging submission"""
    if not user.is_judge or not submission.phase.is_judgable or \
        not submission.judgeable_by(user):
        return {}
    judging_form = (judging_form if judging_form else _get_judging_form(user=user, entry=submission))
    judge_assigned = (JudgeAssignment.objects
                      .filter(judge__user=user, submission=submission)
                      .exists())
    return {
        'judging_form': judging_form,
        'judge_assigned': judge_assigned,
        }


@project_challenge_required
def entry_show(request, project, challenge, entry_id, phase, judging_form=None):
    """Detail of an ``Submission``
    ``SubmissionParent`` acts as an proxy for any of the revisions only
    shows the current revision
    ``phase`` determines the slug on which this ``Submission`` was accesed
    """
    phase = get_phase_or_404(phase)
    try:
        parent = (SubmissionParent.objects.select_related('submission')
                  .get(slug=entry_id, submission__phase__challenge=challenge,
                       submission__phase=phase))
    except SubmissionParent.DoesNotExist:
        raise Http404
    entry = parent.submission
    if not entry.visible_to(request.user):
        raise Http404
    # Voting is saved in the parent
    user_vote = Vote.objects.get_for_user(parent, request.user)
    votes = Vote.objects.get_score(parent)
    # Previous/next entries
    previous_submission = Submission.objects.previous_submission(entry)
    next_submission = Submission.objects.next_submission(entry)
    # Use all the submission ids to sumarize any information required for the
    # project homepage
    submission_ids = list(parent.submissionversion_set.all()
                      .values_list('submission__id', flat=True)) + [entry.id]
    # Cache the awarded badges
    badge_list = (SubmissionBadge.objects.select_related('badge')
                  .filter(is_published=True, submission__in=submission_ids))
    # Cache webcast list
    webcast_list = TimeSlot.objects.filter(is_booked=True,
                                           submission__in=submission_ids)
    context = {
        'project': project,
        'challenge': challenge,
        'entry': entry,
        'links': entry.externallink_set.all() or False,
        'previous': previous_submission or False,
        'next': next_submission or False,
        'user_vote': user_vote,
        'votes': votes['score'],
        'excluded': entry.exclusionflag_set.exists(),
        'webcast_list': webcast_list,
        'badge_list': badge_list,
        'parent': parent,
    }
    # Add extra context to the View. It is on regular django templates it is
    # usually done on template tags. In this case we do it here
    context.update(get_judging_context(request.user, entry, judging_form))
    context.update(get_award_context(entry, request.user))
    return jingo.render(request, 'challenges/show_entry.html', context)


def _get_judging_form(user, entry, data=None, form_class=JudgingForm):
    try:
        judgement = Judgement.objects.get(judge=user.get_profile(),
                                          submission=entry)
        criteria = [a.criterion for a in judgement.answers.all()]
    except Judgement.DoesNotExist:
        judgement = Judgement(judge=user.get_profile(), submission=entry)
        criteria = entry.phase.judgement_criteria.all()

    return form_class(data, instance=judgement, criteria=criteria)


@login_required
@judge_required
@project_challenge_required
def entry_judge(request, project, challenge, pk):
    try:
        submission = Submission.objects.get(id=pk)
    except Submission.DoesNotExist:
        raise Http404
    if request.method == 'GET':
        # Redirect back to the entry view
        # Strictly speaking, this view shouldn't accept GET requests, but in
        # case someone submits theform, gets errors and reloads this URL,
        # redirecting back to the entry seems the sanest choice
        return HttpResponseRedirect(submission.get_absolute_url())
    # Make sure it is only available when the phases is judgable
    if not submission.phase.is_judgable \
        or not submission.judgeable_by(request.user):
        raise Http404
    form = _get_judging_form(data=request.POST, user=request.user,
                             entry=submission, form_class=JudgingForm)
    if form.is_valid():
        form.save()
        messages.success(request,
                         _('Success! Thanks for evaluating the submission.'))
        return HttpResponseRedirect(reverse('entries_assigned'))
    # Pass the form with errors back to the entry detail page
    # Show the entry page with the form (and errors)
    return entry_show(request, project=project.slug, slug=challenge.slug,
                      entry_id=pk, phase=submission.phase_slug,
                      judging_form=form)


def archive_submission(submission, form, link_form, phase):
    """Archive the old ``Submisssion`` and create a new entry for the currrent
    ``Phase`` ``PhaseRound`` combination"""
    previous_submission = submission
    new_submission = Submission(created_by=previous_submission.created_by,
                                category=previous_submission.category,
                                phase=phase)
    # ``Submission`` enters to tne open ``PhaseRound``
    if phase.current_round:
        new_submission.phase_round = phase.current_round
    # Reuse the existing image if one hasn't been provided
    if not form.cleaned_data.get('sketh_note'):
        new_submission.sketh_note = submission.sketh_note
    # Create a new instance of the ``ModelForm`` since we want to duplicate
    # and call whatever mechanisms might be triggered through the form
    new_form = form.__class__(form.data, form.files, instance=new_submission)
    new_submission = new_form.save()
    submission.parent.update_version(new_submission)
    # Duplicate the links sent for this ``Submission``
    create_link = lambda link: ExternalLink.objects.create(
        url=link['url'], name=link['name'], submission=new_submission)
    link_form = [create_link(link) for link in link_form.cleaned_data if link]
    return new_submission


def submission_edit(request, submission, phase, form_class=EntryForm,
                    template='challenges/edit.html', extra_context=None):
    """Updates a given ``Submission``
    Keeps versions the ``Submission``
    If the edit happens after a ``PhaseRound`` is closed it enters the current
    open phase"""
    error_count = 0
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=submission)
        link_form = InlineLinkFormSet(request.POST, instance=submission,
                                      prefix='externals')
        if form.is_valid() and link_form.is_valid():
            if submission.phase == phase \
                and submission.phase_round == phase.current_round:
                # Same ``Phase`` and ``PhaseRound`` update the current phase
                submission = form.save()
                link_form.save()
            else:
                # ``Submission`` enters the new open ``PhaseRound`` and
                # it is duplicated and archived
                submission = archive_submission(submission, form, link_form,
                                                phase)
            messages.success(request, "Your submission has been updated.")
            return HttpResponseRedirect(submission.get_absolute_url())
        else:
            error_count = get_list_count(form.errors,
                                         link_form.non_form_errors())
    else:
        form = form_class(instance=submission)
        link_form = InlineLinkFormSet(instance=submission, prefix='externals')
    context = {
        'form': form,
        'link_form': link_form,
        'error_count': error_count,
        }
    if extra_context:
        context.update(extra_context)
    return jingo.render(request, template, context)


@login_required
@project_challenge_required
def entry_edit(request, project, challenge, pk, phase):
    """Edit ``Submission`` ideas mechanics"""
    phase = get_phase_or_404(phase)
    # Ideation phase must be open
    if not phase or not phase.is_open:
        raise Http404
    form_class = EntryForm if phase.is_ideation else DevelopmentEntryForm
    extra_context = {
        'project': project,
        'challenge': challenge,
        }
    parent = get_submissionparent_or_404(challenge, slug=pk,
                                         submission__phase=phase)
    submission = parent.submission
    if not submission.editable_by(request.user):
        return HttpResponseForbidden()
    # Ideas ``Submissions`` can't be turned into Proposals
    if not submission.phase == phase:
        raise Http404
    return submission_edit(request, submission, phase, form_class=form_class,
                           extra_context=extra_context)


@login_required
@project_challenge_required
def entry_delete(request, project, challenge, pk, phase):
    """Removes a user ``Submission``"""
    phase = get_phase_or_404(phase)
    profile = request.user.get_profile()
    try:
        parent = (SubmissionParent.objects.select_related('submission')
                  .get(submission__pk=pk, submission__phase__challenge=challenge,
                       submission__phase=phase,
                       submission__created_by=profile))
    except SubmissionParent.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        # Remove all the versioned content from the Parent, since
        # the User don't want to keep any versions of this ``Submission``
        for old_submission in parent.submissionversion_set.all():
            # remove submissoin
            old_submission.submission.delete()
            # remove version
            old_submission.delete()
        # Remove the current ``Submission``
        parent.submission.delete()
        # Remove the ``SubmissionParent``
        parent.delete()
        messages.success(request, "Your submission has been deleted.")
        return HttpResponseRedirect(profile.get_absolute_url())
    context = {
        'project': project,
        'challenge': challenge,
        'object': parent.submission,
        'parent': parent,
        }
    return jingo.render(request, 'challenges/delete.html', context)


@login_required
@project_challenge_required
def entry_help(request, project, challenge, entry_id):
    """``Submissions`` that need help"""
    # SubmissionParent acts as an proxy for any of the revisions.
    # and it only shows the current revision
    try:
        parent = (SubmissionParent.objects.select_related('submission')
                  .get(slug=entry_id, submission__phase__challenge=challenge,
                       submission__created_by=request.user.get_profile()))
    except SubmissionParent.DoesNotExist:
        raise Http404
    try:
        help_instance = parent.submissionhelp
    except SubmissionHelp.DoesNotExist:
        help_instance = None
    if request.method == 'POST':
        form = SubmissionHelpForm(request.POST, instance=help_instance)
        instance = form.save(commit=False)
        instance.parent = parent
        instance.save()
        if instance.status == SubmissionHelp.PUBLISHED:
            msg = _('Your message has been posted successfully and is now '
                    'available on your Idea page')
            messages.success(request, msg)
        return HttpResponseRedirect(parent.submission.get_absolute_url())
    else:
        form = SubmissionHelpForm(instance=help_instance)
    context = {'form': form}
    return jingo.render(request, 'challenges/submission_help.html', context)


@project_challenge_required
def entry_help_list(request, project, challenge):
    """Lists all the ``Submissions`` that need help"""
    object_list = SubmissionHelp.objects.get_active()
    page_number = get_page(request.GET)
    paginated_query = get_paginator(object_list, page_number)
    context = {'page': paginated_query}
    return jingo.render(request, 'challenges/submission_help_list.html',
                        context)
