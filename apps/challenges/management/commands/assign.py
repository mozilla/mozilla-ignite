from optparse import make_option

from django.contrib.auth.models import User, Permission
from django.core.management.base import NoArgsCommand
from django.db.models import Q

from challenges.models import Submission


def count_of(thing_list, thing_name, plural_name=None, colon=False):
    """Return a string representing a count of things, given in thing_list."""
    if plural_name is None:
        plural_name = thing_name + 's'
    format = '%d ' + (thing_name if len(thing_list) == 1 else plural_name)
    if colon:
        format += ':'
    return format % len(thing_list)


class Command(NoArgsCommand):
    help = u'Assign unrated entries to random judges.'
    
    option_list = (NoArgsCommand.option_list +
                   (make_option('-n', '--dry-run', action='store_true',
                                help="Just print output: don't assign anything"),))
    
    def handle_noargs(self, verbosity, dry_run, **options):
        verbosity = int(verbosity)  # Django doesn't do this by default
        
        # Running this check manually because we don't want to include
        # superusers unless they've been given explicit permission
        judge_permission = Permission.objects.get(codename='judge_submission')
        judges = User.objects.filter(Q(user_permissions=judge_permission) |
                                     Q(groups__permissions=judge_permission))
        
        is_judged = Q(judgement__isnull=False)
        is_assigned = Q(judgeassignment__isnull=False)
        
        submissions = Submission.objects.exclude(is_judged | is_assigned)
        if verbosity >= 1:
            print count_of(submissions, 'submission',
                           colon=verbosity >= 2 and len(submissions))
            if verbosity >= 2:
                for submission in submissions:
                    print '    %s' % submission.title
        
        if verbosity >= 1:
            print count_of(judges, 'judge',
                           colon=verbosity >= 2 and len(judges))
            if verbosity >= 2:
                for judge in judges:
                    print '    %s [%s]' % (judge.get_profile().display_name,
                                           judge.username)
        if not dry_run:
            print 'This would now do some stuff'
