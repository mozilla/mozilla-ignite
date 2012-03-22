from datetime import datetime, timedelta
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from timeslot.models import Release, TimeSlot

from challenges.models import (Submission, Phase, Challenge, Category,
                               Project, PhaseRound, SubmissionParent)


def create_project(slug, extra_data=None):
    """Creates a project"""
    data = {
        'name': slug.title(),
        'slug': slug,
        'description': '%s description' % slug,
        'allow_participation': True,
        }
    if extra_data:
        data.update(extra_data)
    instance, created = Project.objects.get_or_create(**data)
    return instance


def create_challenge(slug, project, extra_data=None):
    """Creates a challenge for the project"""
    data = {
        'project': project,
        'title': slug.title(),
        'slug': slug,
        'start_date': datetime.utcnow(),
        'end_date': datetime.utcnow() + timedelta(days=30),
        }
    if extra_data:
        data.update(extra_data)
    instance, created = Challenge.objects.get_or_create(**data)
    return instance


def create_phase(slug, challenge, extra_data=None):
    """Creates a phase for the challenge"""
    data = {
        'challenge': challenge,
        'name': slug,
        'order': 1,
        }
    if extra_data:
        data.update(extra_data)
    instance, created = Phase.objects.get_or_create(**data)
    return instance


def create_user(handle):
    """Helper to create Users with a profile"""
    email = '%s@%s.com' % (handle, handle)
    user = User.objects.create_user(handle, email, handle)
    profile = user.get_profile()
    # middleware needs a name if not will redirect to edit
    profile.name = handle.title()
    profile.save()
    return profile


def create_category(slug, extra_data=None):
    """Creates a category"""
    data = {
        'name': slug.title(),
        'slug': slug,
        }
    if extra_data:
        data.update(data)
    instance, created = Category.objects.get_or_create(**data)
    return instance


def create_submission(title, profile, phase, extra_data=None, parent=True):
    """Creates a submission"""
    data = {
        'created_by': profile,
        'phase': phase,
        'category': create_category('Lorem'),
        'title': title,
        }
    if extra_data:
        data.update(extra_data)
    instance, created = Submission.objects.get_or_create(**data)
    if parent:
        SubmissionParent.objects.get_or_create(submission=instance)
    return instance


def create_phase_round(name, phase, extra_data=None):
    data = {
        'name': name,
        'phase': phase,
        'start_date': datetime.utcnow(),
        'end_date': datetime.utcnow() + timedelta(hours=1),
        }
    if extra_data:
        data.update(extra_data)
    instance, created = PhaseRound.objects.get_or_create(**data)
    return instance

def create_judge(handle):
    judge = create_user(handle)
    submission_type = ContentType.objects.get_for_model(Submission)
    judge_permission, created = (Permission.objects
                                 .get_or_create(codename='judge_submission',
                                                content_type=submission_type))
    judge.user.user_permissions.add(judge_permission)
    return judge


def create_release(name, is_current, phase, extra_data=None):
    """Helper to create releases"""
    data = {'name': name, 'is_current': is_current, 'phase': phase}
    if extra_data:
        data.update(extra_data)
    instance, created = Release.objects.get_or_create(**data)
    return instance

def create_timeslot(release, **kwargs):
    """Helper to add ``TimeSlots`` with the minium required data"""
    # booking of timeslots start at least 24 hours in advance
    start_date = datetime.utcnow() + timedelta(hours=25)
    end_date = start_date + timedelta(minutes=60)
    defaults = {
        'start_date': start_date,
        'end_date': end_date,
        'release': release,
        }
    if kwargs:
        defaults.update(kwargs)
    return TimeSlot.objects.create(**defaults)

