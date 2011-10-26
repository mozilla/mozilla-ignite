from django.shortcuts import get_object_or_404
import jingo

from challenges.models import Challenge
from projects.models import Project


def show(request, project, slug):
    challenge = get_object_or_404(Challenge, slug=slug)
    project = get_object_or_404(Project, slug=project)
    return jingo.render(request, 'challenges/show.html', {
        'p11n': challenge,
        'project': project,
        'entries': [],
    })
