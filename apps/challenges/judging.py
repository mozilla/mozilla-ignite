import random

from itertools import cycle, izip
from django.contrib.auth.models import User, Permission
from django.db.models import Q

from challenges.models import Submission, JudgeAssignment


def get_judge_profiles():
    """Return the profiles of all current judges."""
    # Running this check manually because we don't want to include
    # superusers unless they've been given explicit permission
    judge_permission = Permission.objects.get(codename='judge_submission')
    judges = User.objects.filter(Q(user_permissions=judge_permission) |
                                 Q(groups__permissions=judge_permission))
    return [j.get_profile() for j in judges]


def get_submissions(phase, phase_round=None):
    """Return the submissions eligible for assignment."""
    is_judged = Q(judgement__isnull=False)
    is_assigned = Q(judgeassignment__isnull=False)
    return (Submission.objects.eligible(phase, phase_round)
            .exclude(is_judged | is_assigned))


def get_assignments(submissions, judge_profiles, commit, judges_per_submission):
    """Assign the given submissions evenly between the given judges.
    Return a list of JudgeAssignment objects."""
    judge_profiles = list(judge_profiles)
    random.shuffle(judge_profiles)
    assert len(judge_profiles) >= judges_per_submission
    judge_sequences = [cycle(judge_profiles) for j in range(judges_per_submission)]
    # Offset each judge sequence by 1
    for offset, sequence in enumerate(judge_sequences):
        for _ in xrange(offset):
            sequence.next()
    pairings = izip(submissions, izip(*judge_sequences))
    assignments = []
    for submission, judge_list in pairings:
        for judge in judge_list:
            assignment = JudgeAssignment(submission=submission, judge=judge)
            if commit:
                assignment.save()
            assignments.append(assignment)
    return assignments

