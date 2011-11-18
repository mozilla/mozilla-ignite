from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.forms.formsets import formset_factory
import jingo
from tower import ugettext as _

from challenges.forms import EntryForm, EntryLinkForm
from challenges.models import Challenge, Phase, Submission, ExternalLink
from projects.models import Project


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
    LinkFormSet = formset_factory(EntryLinkForm, extra=2)
    form_errors = False 
    if request.method == 'POST':
        form = EntryForm(data=request.POST,
            files=request.FILES)
        link_form = LinkFormSet(request.POST, prefix="externals")
        if form.is_valid():
            entry = form.save(commit=False)
            entry.created_by = profile
            entry.phase = phase
            entry.save()
            if link_form.is_valid():
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
            form_errors = {}
            # this feels horrible but I think required to create a custom error list
            for k in form.errors.keys():
                form_errors[k] =  form.errors[k].as_text()
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
    return jingo.render(request, 'challenges/show_entry.html', {
        'project': project,
        'challenge': challenge,
        'entry': entry
    })
