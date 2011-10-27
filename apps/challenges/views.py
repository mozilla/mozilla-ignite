from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
import jingo
from tower import ugettext as _

from challenges.forms import EntryForm
from challenges.models import Challenge
from projects.models import Project


def show(request, project, slug, template_name='challenges/show.html'):
    """Show an individual project challenge."""
    project = get_object_or_404(Project, slug=project)
    challenge = get_object_or_404(project.challenge_set, slug=slug)
    return jingo.render(request, template_name, {
        'p11n': challenge,
        'project': project,
        'entries': challenge.submission_set.all(),
    })


def entries_all(request, project, slug):
    """Show all entries (submissions) to a challenge."""
    return show(request, project, slug, template_name='challenges/all.html')


# Stub views to keep the URL resolvers happy


def create_entry(request, project, slug):
    project = get_object_or_404(Project, slug=project)
    challenge = get_object_or_404(Challenge, slug=slug)
    profile = request.user.get_profile()
    form_errors = False
    if request.method == 'POST':
        form = EntryForm(data=request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.challenge = challenge
            entry.save()
            # double save needed to add in m2m key
            entry.created_by = form.cleaned_data['created_by']
            if not profile in form.cleaned_data['created_by']:
                entry.created_by.add(profile)
            entry.save()
            msg = _('Your entry has been posted successfully and is now available for public review')
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('challenge_show', kwargs={
                'project': project.slug,
                'slug': challenge.slug
            }))
        else:
            form_errors = {}
            # this feels horrible but I think required to create a custom error list
            for k in form.errors.keys():
                form_errors[k] =  form.errors[k].as_text()
    else:
        form = EntryForm()
    return jingo.render(request, 'challenges/create.html', {
        'project': project,
        'p11n': challenge,
        'form': form,
        'errors': form_errors
    })


def entry_show(request):
    pass
