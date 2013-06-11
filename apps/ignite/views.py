from django.shortcuts import get_object_or_404
import jingo
import waffle

from django.contrib.auth.models import User
from challenges.models import Submission, Category
from projects.models import Project
from blogs.models import BlogEntry
from events.models import Event


def splash(request, project, slug, template_name='ignite/splash.html'):
    """Show an individual project challenge."""
    project = get_object_or_404(Project, slug=project)
    challenge = get_object_or_404(project.challenge_set, slug=slug)
    num_blogs = 3
    # have we announced the winners yet - switch template
    if waffle.switch_is_active('announce_winners'):
        template_name = 'ignite/homepage-winners.html'
        num_blogs = 5
    blogs = BlogEntry.objects.filter(
        page='splash'
    ).order_by("-updated",)[:num_blogs]
    # if the dev challenge is open we want to only show dev entries
    if request.development.is_open:
        entries = (Submission.objects.visible()
                                 .filter(phase__challenge=challenge)
                                 .filter(phase__name="Development")
                                 .order_by("?"))
        num_entries = len(entries)
        entries_from = 'apps'
        if num_entries < 5:
            entries = (Submission.objects.visible()
                                 .filter(phase__challenge=challenge)
                                 .filter(phase__name="Ideation")
                                 .order_by("?"))
            entries_from = 'ideas'
    else:
        entries = (Submission.objects.visible()
                                 .filter(phase__challenge=challenge)
                                 .filter(phase__name="Ideation")
                                 .order_by("?"))
        entries_from = 'ideas'

    event_list = Event.objects.get_featured()[:5]
    return jingo.render(request, template_name, {
        'challenge': challenge,
        'project': project,
        'phases': list(enumerate(challenge.phases.all(), start=1)),
        'entries': entries[:5],
        'categories': Category.objects.all(),
        'blogs': blogs,
        'event_list': event_list,
        'entries_from': entries_from,
    })


def about(request, project, slug, template_name='ignite/about.html'):
    if waffle.switch_is_active('announce_winners'):
        template_name = 'ignite/about-winners.html'
    return jingo.render(request, template_name)


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


def terms_development(request, project, slug, template_name='static/terms_conditions_development.html'):
    return jingo.render(request, template_name, {})


def fail(request, template_name='404.html'):
    return jingo.render(request, template_name, {}, status=404)


def app_fail(request, template_name='500.html'):
    return jingo.render(request, template_name, {}, status=500)


def action_unavailable_response(request, message=None,
                                template_name="action_unavailable.html"):
    """Generic page for unavailable actions"""
    context = {'message': message}
    return jingo.render(request, template_name, context, status=403)
