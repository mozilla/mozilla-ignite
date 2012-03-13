from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.db.models import Q
from django.http import Http404


def judge_required(func):
    """Allows only users marked as judges to go through"""
    def _decorated(request, *args, **kwargs):
        # Running this check manually because we don't want to include
        # superusers unless they've been given explicit permission
        judge_permission = Permission.objects.get(codename=settings.JUDGE_PERMISSION)
        try:
            user = User.objects.get(Q(user_permissions=judge_permission) |
                                    Q(groups__permissions=judge_permission),
                                    id=request.user.id)
        except User.DoesNotExist:
            raise Http404
        return func(request, *args, **kwargs)
    return _decorated
