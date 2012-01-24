from django.contrib.auth.models import User, Permission
from django.core.management.base import NoArgsCommand
from django.db.models import Q


class Command(NoArgsCommand):
    help = u'Assign unrated entries to random judges.'

    def handle_noargs(self, **options):
        
        # Running this check manually because we don't want to include
        # superusers unless they've been given explicit permission
        judge_permission = Permission.objects.get(codename='judge_submission')
        judges = User.objects.filter(Q(user_permissions=judge_permission) |
                                     Q(groups__permissions=judge_permission))
        
        if len(judges) == 1:
            print '%d judge:' % len(judges)
        else:
            print '%d judges:' % len(judges)
        for judge in judges:
            print '    %s [%s]' % (judge.get_profile().display_name,
                                   judge.username)
