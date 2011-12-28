from django.shortcuts import get_object_or_404
import jingo

from challenges.models import Submission, Category
from projects.models import Project
from blogs.models import BlogEntry


def splash(request, project, slug, template_name='challenges/show.html'):
    """Show an individual project challenge."""
    project = get_object_or_404(Project, slug=project)
    challenge = get_object_or_404(project.challenge_set, slug=slug)
    entries = Submission.objects.filter(
        phase__challenge=challenge
    ).exclude(
        is_draft=True
    ).extra(
        order_by="?"
    )
    blogs = BlogEntry.objects.filter(
        page='splash'
    )

    return jingo.render(request, 'ignite/splash.html', {
        'challenge': challenge,
        'project': project,
        'phases': list(enumerate(challenge.phases.all(), start=1)),
        'entries': entries[:10],
        'categories': Category.objects.get_active_categories(),
        'blogs': blogs
    })
