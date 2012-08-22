import sys
from datetime import datetime
from itertools import cycle, izip
from optparse import make_option
import random

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.core.management.base import NoArgsCommand, CommandError
from django.db.models import Q

from challenges.models import Submission, JudgeAssignment, Phase, PhaseRound
from challenges.judging import (get_judge_profiles, get_submissions,
                                get_assignments)

def count_of(thing_list, thing_name, plural_name=None, colon=False):
    """Return a string representing a count of things, given in thing_list.
    
    Example:
    
    >>> count_of([1, 2, 3], 'number')
    '3 numbers'
    >>> count_of([1], 'number')
    '1 number'
    >>> count_of(['salmon', 'carp'], 'fish', 'fishies')
    '2 fishies'
    
    """
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
        verbose, quiet = verbosity >= 2, verbosity < 1
        option_list = []
        now = datetime.utcnow()
        print("IMPORTANT: Only past Phases and Rounds can be assigned for "
              ". Judging available Phases are:\n")
        for phase in Phase.objects.all():
            round_list = phase.phaseround_set.all()
            if round_list:
                # We can't assign challenges that are not finished
                option_list += [i for i in round_list if i.end_date < now]
            else:
                if phase.end_date < now:
                    option_list.append(phase)
        for i, option in enumerate(option_list):
            if isinstance(option, PhaseRound):
                print "%s) %s: %s" % (i, option.phase, option.name)
            else:
                print "%s) %s" % (i, option)
        selection = raw_input('\nSelect Phase or Round to assign: ')
        try:
            selected = option_list[int(selection)]
        except (ValueError, IndexError):
            raise CommandError('Select a valid option')
        if isinstance(selected, PhaseRound):
            phase, phase_round = selected.phase, selected
        else:
            phase, phase_round = selected, None
        submissions = get_submissions(phase, phase_round)
        if not quiet:
            print count_of(submissions, 'submission',
                           colon=verbosity >= 2 and len(submissions)), "to be assigned"
            if verbose:
                for submission in submissions:
                    print '    %s' % submission.title
        judge_profiles = get_judge_profiles()
        if not quiet:
            print count_of(judge_profiles, 'judge',
                           colon=verbosity >= 2 and len(judge_profiles)), "available"
            if verbose:
                for judge in judge_profiles:
                    print '    %s [%s]' % (judge.display_name,
                                           judge.user.username)
        if submissions and len(judge_profiles) < settings.JUDGES_PER_SUBMISSION:
            print "You don't have enough judges assigned: you need %d" % \
                  settings.JUDGES_PER_SUBMISSION
            sys.exit(1)
        
        assignments = get_assignments(submissions, judge_profiles,
                                      commit=not dry_run,
                                      judges_per_submission=settings.JUDGES_PER_SUBMISSION)
        if verbose:
            for assignment in assignments:
                print '"%s" goes to %s' % (assignment.submission.title,
                                           assignment.judge.display_name)
