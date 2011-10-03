import jingo

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from tower import ugettext as _

from projects.models import Project
from participation.models import Participation, Entry
from participation.forms import EntryForm


def show(request, project, slug):
    participation = get_object_or_404(Participation, slug=slug)
    project = get_object_or_404(Project, slug=project)
    entries = Entry.objects.filter(participation=participation).order_by('-id') or False
    return jingo.render(request, 'participation/show.html', {
        'p11n': participation,
        'project': project,
        'entries': entries
    })

def entries_all(request, project, slug):
    project = get_object_or_404(Project, slug=project)
    p11n = get_object_or_404(Participation, slug=slug)
    entries = Entry.objects.filter(participation=p11n).order_by('-id') or False
    return jingo.render(request, 'participation/all.html', {
        'project': project,
        'p11n': p11n,
        'entries': entries
    })

def create_entry(request, project, slug):
    project = get_object_or_404(Project, slug=project)
    participation = get_object_or_404(Participation, slug=slug)
    profile = request.user.get_profile()
    form_errors = False
    if request.method == 'POST':
        form = EntryForm(data=request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.participation = participation
            entry.save()
            # double save needed to add in m2m key
            entry.created_by = form.cleaned_data['created_by']
            if not profile in form.cleaned_data['created_by']:
                entry.created_by.add(profile)
            entry.save()
            msg = _('Your entry has now been posted successfully and is now availiable for public review')
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('participation_show', kwargs={
                'project': project.slug,
                'slug': participation.slug
            }))
        else:
            form_errors = {}
            # this feels horrible but I think required to create a custom error list
            for k in form.errors.keys():
                form_errors[k] =  form.errors[k].as_text()
    else:    
        form = EntryForm()
    return jingo.render(request, 'participation/create.html', {
        'project': project,
        'p11n': participation,
        'form': form,
        'errors': form_errors
    })

def entry_show(request, project, slug, entry_id):
    project = get_object_or_404(Project, slug=project)
    p11n = get_object_or_404(Participation, slug=slug)
    entry = p11n.entry_set.get(pk=entry_id)
    return jingo.render(request, 'participation/show_entry.html', {
        'project': project,
        'p11n': p11n,
        'entry': entry
    })

