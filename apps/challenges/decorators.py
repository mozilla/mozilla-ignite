import functools

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden


def judge_required(func):
    """Allows only users marked as judges to go through"""
    @functools.wraps(func)
    def _decorated(request, *args, **kwargs):
        # Running this check manually because we don't want to include
        # superusers unless they've been given explicit permission
        judge_permission = (Permission.objects
                            .get(codename=settings.JUDGE_PERMISSION))
        try:
            User.objects.get(Q(user_permissions=judge_permission) |
                             Q(groups__permissions=judge_permission),
                             id=request.user.id)
        except User.DoesNotExist:
            raise Http404
        return func(request, *args, **kwargs)
    return _decorated

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
