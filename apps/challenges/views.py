from django.shortcuts import get_object_or_404
import jingo

from challenges.models import Challenge
from projects.models import Project


def show(request, project, slug):
    project = get_object_or_404(Project, slug=project)
    challenge = get_object_or_404(project.challenge_set, slug=slug)
    return jingo.render(request, 'challenges/show.html', {
        'p11n': challenge,
        'project': project,
        'entries': [],
    })
