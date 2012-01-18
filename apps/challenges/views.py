import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView, DeleteView
import jingo
from tower import ugettext as _
from voting.models import Vote

from challenges.forms import EntryForm, EntryLinkForm, InlineLinkFormSet, \
                             JudgingForm
from challenges.models import Challenge, Phase, Submission, Category, \
                              ExternalLink, Judgement, JudgingCriterion
from projects.models import Project

challenge_humanised = {
    'title': 'Title',
    'brief_description': 'Summary',
    'description': 'Full description',
    'sketh_note': 'Napkin sketch',
    'category': 'Category',
}


LOGGER = logging.getLogger(__name__)


def show(request, project, slug, template_name='challenges/show.html', category=False):
    """Show an individual project challenge."""
    project = get_object_or_404(Project, slug=project)
    challenge = get_object_or_404(project.challenge_set, slug=slug)
    """ Pagination options """
    entry_set = Submission.objects.filter(phase__challenge=challenge)
    if category:
        entry_set = entry_set.filter(category__name=category)
    paginator = Paginator(entry_set, 25)

    try:
        page = int(request.GET.get('page', '1'))
    except (ValueError, TypeError):
        page = 1

    try:
        entries = paginator.page(page)
    except (EmptyPage, InvalidPage):
        entries = paginator.page(paginator.num_pages)

    return jingo.render(request, template_name, {
        'challenge': challenge,
        'project': project,
        'phases': list(enumerate(challenge.phases.all(), start=1)),
        'entries': entries,
        'categories': Category.objects.get_active_categories(),
        'category': category,
    })


def entries_all(request, project, slug):
    """Show all entries (submissions) to a challenge."""
    return show(request, project, slug, template_name='challenges/all.html')


def entries_category(request, project, slug, category):
    """Show all entries to a specific category"""
    return show(request, project, slug, template_name='challenges/all.html', category=category)


def extract_form_errors(form, link_form):
    form_errors = {}
    # this feels horrible but I think required to create a custom error list
    for k in form.errors.keys():
        humanised_key = challenge_humanised[k]
        form_errors[humanised_key] =  form.errors[k].as_text()
    if not link_form.is_valid():
        form_errors['External links'] = "* Please provide a valid URL and name for each link provided"
    
    return form_errors


@login_required
def create_entry(request, project, slug):
    project = get_object_or_404(Project, slug=project)
    
    try:
        phase = Phase.objects.get_current_phase(slug)[0]
    except IndexError:
        raise Http404
    
    profile = request.user.get_profile()
    LinkFormSet = formset_factory(EntryLinkForm, extra=2)
    form_errors = False 
    if request.method == 'POST':
        form = EntryForm(data=request.POST,
            files=request.FILES)
        link_form = LinkFormSet(request.POST, prefix="externals")
        if form.is_valid() and link_form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = profile
            entry.phase = phase
            entry.save()
            for link in link_form.cleaned_data:
                if all(i in link for i in ("name", "url")): 
                    ExternalLink.objects.create(
                        name = link['name'],
                        url = link['url'],
                        submission = entry
                    )
            msg = _('Your entry has been posted successfully and is now available for public review')
            messages.success(request, msg)
            return HttpResponseRedirect(phase.challenge.get_absolute_url())
        else:
            form_errors = extract_form_errors(form, link_form)
    else:
        form = EntryForm()
        link_form = LinkFormSet(prefix='externals')
    return jingo.render(request, 'challenges/create.html', {
        'project': project,
        'challenge': phase.challenge,
        'form': form,
        'link_form': link_form,
        'errors': form_errors
    })


def entry_show(request, project, slug, entry_id):
    project = get_object_or_404(Project, slug=project)
    challenge = get_object_or_404(project.challenge_set, slug=slug)
    entry = get_object_or_404(Submission.objects, pk=entry_id,
                              phase__challenge=challenge)
    # Sidebar
    ## Voting
    user_vote = Vote.objects.get_for_user(entry, request.user)
    votes = Vote.objects.get_score(entry)
    
    ## Previous/next modules
    try:
        previous = entry.get_previous_by_created_on()
    except Submission.DoesNotExist:
        previous = False
    try:
        next = entry.get_next_by_created_on()
    except Submission.DoesNotExist:
        next = False
    
    # Judging
    if entry.judgeable_by(request.user):
        try:
            judgement = Judgement.objects.get(judge=request.user.get_profile(),
                                              submission=entry)
            criteria = [a.criterion for a in judgement.answers.all()]
        except Judgement.DoesNotExist:
            judgement = None
            criteria = entry.phase.judgement_criteria.all()
            
        judging_form = JudgingForm(instance=judgement, criteria=criteria)
    else:
        judging_form = None
    
    return jingo.render(request, 'challenges/show_entry.html', {
        'project': project,
        'challenge': challenge,
        'entry': entry,
        'previous': previous or False,
        'next': next or False,
        'user_vote': user_vote,
        'votes': votes['score'],
        'judging_form': judging_form,
    })


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


class SingleSubmissionMixin(SingleObjectMixin):
    """Mixin for views operating on a single submission.
    
    This mixin handles looking up the submission and checking user permissions.
    
    """
    
    def _get_challenge(self):
        return get_object_or_404(Challenge,
                                 project__slug=self.kwargs['project'],
                                 slug=self.kwargs['slug'])
    
    def get_queryset(self):
        return Submission.objects.filter(phase__challenge=self._get_challenge())
    
    def get_object(self, *args, **kwargs):
        obj = super(SingleSubmissionMixin, self).get_object(*args, **kwargs)
        if not self._check_permission(obj, self.request.user):
            raise PermissionDenied()
        return obj
    
    def _check_permission(self, submission, user):
        """Check the given user is allowed to use this view.
        
        Return True if the operation is allowed; otherwise return False.
        
        Inheriting views should override this with the appropriate permission
        checks.
        
        """
        return True


class EditEntryView(UpdateView, JingoTemplateMixin, SingleSubmissionMixin):
    
    form_class = EntryForm
    link_form_class = InlineLinkFormSet
    template_name = 'challenges/edit.html'
    
    def _check_permission(self, submission, user):
        return submission.editable_by(user)
    
    # The following two methods are analogous to Django's generic form methods
    
    def get_link_form(self, link_form_class):
        return link_form_class(**self.get_link_form_kwargs())
    
    def get_link_form_kwargs(self):
        form_kwargs = super(EditEntryView, self).get_form_kwargs()
        # Initial data doesn't apply to formsets
        del form_kwargs['initial']
        form_kwargs.update(instance=self.object, prefix='externals')
        return form_kwargs
    
    def get_forms(self):
        """Return the forms available to this view as a dictionary."""
        form = self.get_form(self.get_form_class())
        link_form = self.get_link_form(self.link_form_class)
        return {'form': form, 'link_form': link_form}
    
    def get(self, request, *args, **kwargs):
        """Respond to a GET request by displaying the edit form."""
        self.object = self.get_object()
        
        context = self.get_context_data(**self.get_forms())
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        """Handle a POST request.
        
        If the forms are both valid, save them and redirect to the success URL.
        If either form is invalid, render the form with the errors displayed.
        
        """
        self.object = self.get_object()
        
        forms = self.get_forms()
        form, link_form = forms['form'], forms['link_form']
        
        if form.is_valid() and link_form.is_valid():
            return self.form_valid(form, link_form)
        else:
            return self.form_invalid(form, link_form)
    
    def form_valid(self, form, link_form):
        response = super(EditEntryView, self).form_valid(form)
        link_form.save()
        return response
    
    def form_invalid(self, form, link_form):
        """Display the form with errors."""
        form_errors = extract_form_errors(form, link_form)
        context = self.get_context_data(form=form, link_form=link_form,
                                        errors=form_errors)
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super(EditEntryView, self).get_context_data(**kwargs)
        context['challenge'] = self._get_challenge()
        context['project'] = context['challenge'].project
        return context
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EditEntryView, self).dispatch(*args, **kwargs)


entry_edit = EditEntryView.as_view()


class DeleteEntryView(DeleteView, JingoTemplateMixin, SingleSubmissionMixin):
    
    template_name = 'challenges/delete.html'
    success_url = '/'
    
    def _check_permission(self, submission, user):
        return submission.deletable_by(user)
    
    def get_context_data(self, **kwargs):
        context = super(DeleteEntryView, self).get_context_data(**kwargs)
        context['challenge'] = self._get_challenge()
        context['project'] = context['challenge'].project
        return context
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteEntryView, self).dispatch(*args, **kwargs)


entry_delete = DeleteEntryView.as_view()
