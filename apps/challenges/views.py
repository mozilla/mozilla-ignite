from django.shortcuts import get_object_or_404
import jingo

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


def create_entry(request):
    pass


def entry_show(request):
    pass
