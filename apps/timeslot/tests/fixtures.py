from datetime import datetime, timedelta
from django.contrib.admin.models import User

from timeslot.models import Release
from challenges.models import (Submission, Phase, Challenge, Category,
                               Project, PhaseRound)


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


def create_submission(title, profile, phase, extra_data=None):
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
    return PhaseRound.objects.create(**data)


def create_release(name, is_current, extra_data=None):
    """Helper to create releases"""
    data = {'name': name, 'is_current': is_current}
    if extra_data:
        data.update(extra_data)
    instance, created = Release.objects.get_or_create(**data)
    return instance
