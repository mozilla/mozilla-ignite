from django.shortcuts import get_object_or_404

import jingo

from projects.models import Project
from participation.models import Participation, Entry
from participation.forms import EntryForm

def show(request, project, slug):
    participation = get_object_or_404(Participation, slug=slug)
    project = get_object_or_404(Project, slug=project)
    entries = Entry.objects.filter(participation=participation) or False
    return jingo.render(request, 'participation/show.html', {
        'p11n': participation,
        'project': project,
        'entries': entries
    })

def create_entry(request, project, slug):
    project = get_object_or_404(Project, slug=project)
    participation = get_object_or_404(Participation, slug=slug)
    form = EntryForm()
    return jingo.render(request, 'participation/create.html', {
        'project': project,
        'p11n': participation,
        'form': form
    })
