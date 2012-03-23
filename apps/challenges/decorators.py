import functools

from challenges.models import Challenge
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User, Permission
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden


judge_required = permission_required('challenges.judge_submission')


def phase_required(func=None, methods_allowed=None, is_open=True):
    """Forbids access to the wrapped view when the phase is not open, by default
    blocks all methods
    Usage:
    - Allow only get
    @phase_open_required(methods_allowed=['GET'])
    - Deny all methods
    @phase_open_required
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            allowed = [] if not methods_allowed else methods_allowed
            # Determine which phase state is blacklisted open or closed
            if is_open:
                condition = not request.phase['is_open']
            else:
                condition = request.phase['is_open']
            if condition and not request.method in allowed:
                return HttpResponseForbidden()
            return func(request, *args, **kwargs)
        return wrapper
    if func is None:
        return decorator
    else:
        return decorator(func)


def phase_open_required(func=None, methods_allowed=None):
    return phase_required(func=func, methods_allowed=methods_allowed,
                          is_open=True)


def phase_closed_required(func=None, methods_allowed=None):
    return phase_required(func=func, methods_allowed=methods_allowed,
                          is_open=False)


def project_challenge_required(func):
    """Makes sure a valid project and a challenge are passed to a view"""
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        if not all(['project' in kwargs, 'slug' in kwargs]):
            raise ValueError('``project_challenge_required`` decorator '
                             'requires ``slug`` and ``project`` arguments'
                             ' as part of the view')
        project_slug = kwargs.pop('project')
        challenge_slug = kwargs.pop('slug')
        # Make sure we have a challenge and a project by those slugs
        try:
            challenge = (Challenge.objects.select_related('project')
                         .get(project__slug=project_slug,
                              slug=challenge_slug))
        except Challenge.DoesNotExist:
            raise Http404
        # pass the challenge and project instances to the view
        return func(request, challenge.project, challenge, *args, **kwargs)
    return wrapper
