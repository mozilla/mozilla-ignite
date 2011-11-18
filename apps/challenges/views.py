import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView
from django.views.generic.base import TemplateResponseMixin
import jingo
from tower import ugettext as _

from challenges.forms import EntryForm
from challenges.models import Challenge, Phase, Submission
from projects.models import Project


LOGGER = logging.getLogger(__name__)


def show(request, project, slug, template_name='challenges/show.html'):
    """Show an individual project challenge."""
    project = get_object_or_404(Project, slug=project)
    challenge = get_object_or_404(project.challenge_set, slug=slug)
    return jingo.render(request, template_name, {
        'challenge': challenge,
        'project': project,
        'phases': list(enumerate(challenge.phases.all(), start=1)),
        'entries': Submission.objects.filter(phase__challenge=challenge),
    })


def entries_all(request, project, slug):
    """Show all entries (submissions) to a challenge."""
    return show(request, project, slug, template_name='challenges/all.html')


@login_required
def create_entry(request, project, slug):
    project = get_object_or_404(Project, slug=project)
    
    # Quick hack to get around the current inability to obtain current phase
    try:
        phase = Phase.objects.filter(challenge__slug=slug)[0]
    except IndexError:
        raise Http404
    
    profile = request.user.get_profile()
    form_errors = False
    if request.method == 'POST':
        form = EntryForm(data=request.POST,
            files=request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = profile
            entry.phase = phase
            entry.save()
            msg = _('Your entry has been posted successfully and is now available for public review')
            messages.success(request, msg)
            return HttpResponseRedirect(phase.challenge.get_absolute_url())
        else:
            form_errors = {}
            # this feels horrible but I think required to create a custom error list
            for k in form.errors.keys():
                form_errors[k] =  form.errors[k].as_text()
    else:
        form = EntryForm()
    return jingo.render(request, 'challenges/create.html', {
        'project': project,
        'challenge': phase.challenge,
        'form': form,
        'errors': form_errors
    })


def entry_show(request, project, slug, entry_id):
    project = get_object_or_404(Project, slug=project)
    challenge = get_object_or_404(project.challenge_set, slug=slug)
    entry = get_object_or_404(Submission.objects, pk=entry_id,
                              phase__challenge=challenge)
    return jingo.render(request, 'challenges/show_entry.html', {
        'project': project,
        'challenge': challenge,
        'entry': entry
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


class EditEntryView(UpdateView, JingoTemplateMixin):
    
    form_class = EntryForm
    template_name = 'challenges/edit.html'
    
    def _get_challenge(self):
        return get_object_or_404(Challenge,
                                 project__slug=self.kwargs['project'],
                                 slug=self.kwargs['slug'])
    
    def get_queryset(self):
        return Submission.objects.filter(phase__challenge=self._get_challenge())
    
    def get_object(self, *args, **kwargs):
        obj = super(EditEntryView, self).get_object(*args, **kwargs)
        if not obj.editable_by(self.request.user):
            raise PermissionDenied()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super(EditEntryView, self).get_context_data(**kwargs)
        context['challenge'] = self._get_challenge()
        context['project'] = context['challenge'].project
        return context
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EditEntryView, self).dispatch(*args, **kwargs)


entry_edit = EditEntryView.as_view()
