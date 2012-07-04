from django.shortcuts import get_object_or_404
import jingo

from django.contrib.auth.models import User
from challenges.models import Submission, Category
from projects.models import Project
from blogs.models import BlogEntry
from events.models import Event


def splash(request, project, slug, template_name='ignite/splash.html'):
    """Show an individual project challenge."""
    project = get_object_or_404(Project, slug=project)
    challenge = get_object_or_404(project.challenge_set, slug=slug)
    blogs = BlogEntry.objects.filter(
        page='splash'
    ).order_by("-updated",)[:3]
    entries = (Submission.objects.visible()
                                 .filter(phase__challenge=challenge)
                                 .order_by("?"))
    event_list = Event.objects.get_featured()[:5]
    return jingo.render(request, template_name, {
        'challenge': challenge,
        'project': project,
        'phases': list(enumerate(challenge.phases.all(), start=1)),
        'entries': entries[:5],
        'categories': Category.objects.all(),
        'blogs': blogs,
        'event_list': event_list,
    })


def about(request, project, slug):
    return jingo.render(request, 'ignite/about.html')


def judges(request, project, slug, template_name='challenges/all_judges.html'):
    """ List all judges we have in the system """
    profiles = []
    for judge in User.objects.filter(groups__name='Judges'):
        profiles.append(judge.get_profile())

    return jingo.render(request, 'ignite/judges.html', {
        'profiles': profiles
    })


def terms(request, project, slug, template_name='static/terms_conditions.html'):
    return jingo.render(request, template_name, {})


def fail(request, template_name='404.html'):
    return jingo.render(request, template_name, {}, status=404)

 
def app_fail(request, template_name='500.html'):
    return jingo.render(request, template_name, {}, status=500)

