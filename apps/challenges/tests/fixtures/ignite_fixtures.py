from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from challenges.models import (Submission, Phase, Challenge, Category,
                               Project, PhaseRound, SubmissionParent)


def create_project(**kwargs):
    slug = settings.IGNITE_PROJECT_SLUG
    defaults = {
        'name': slug.title(),
        'slug': slug,
        'description': '%s description' % slug,
        'allow_participation': True,
        }
    if kwargs:
        defaults.update(defaults)
    instance, created = Project.objects.get_or_create(**defaults)
    return instance


def create_challenge(**kwargs):
    slug = settings.IGNITE_CHALLENGE_SLUG
    now = datetime.utcnow()
    defaults = {
        'project': kwargs['project'] if 'project' in kwargs else create_project(),
        'title': slug.title(),
        'slug': slug,
        'start_date': now,
        'end_date': now,
        }
    if kwargs:
        defaults.update(kwargs)
    instance, created = Challenge.objects.get_or_create(**defaults)
    return instance


def create_phase(**kwargs):
    defaults = {
        'challenge': kwargs['challenge'] if 'challenge' in kwargs else create_challenge(),
        'name': 'Ideation',
        'order': 1,
        }
    if kwargs:
        defaults.update(kwargs)
    instance, created = Phase.objects.get_or_create(**defaults)
    return instance


def create_phase_round(**kwargs):
    now = datetime.utcnow()
    defaults = {
        'name': 'Round A',
        'phase': kwargs['phase'] if 'phase' in kwargs else create_phase(name='Development'),
        'start_date': now,
        'end_date': now,
        }
    if kwargs:
        defaults.update(kwargs)
    instance, created = PhaseRound.objects.get_or_create(**defaults)
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


def create_judge(handle):
    judge = create_user(handle)
    submission_type = ContentType.objects.get_for_model(Submission)
    judge_permission, created = (Permission.objects
                                 .get_or_create(codename='judge_submission',
                                                content_type=submission_type))
    judge.user.user_permissions.add(judge_permission)
    return judge


def create_category(**kwargs):
    slug = 'miscellaneous'
    defaults = {
        'name': slug.title(),
        'slug': slug,
        }
    if kwargs:
        defaults.update(kwargs)
    instance, created = Category.objects.get_or_create(**defaults)
    return instance


def create_submission(with_parent=True, **kwargs):
    created_by = kwargs['created_by'] if 'created_by' in kwargs else create_user('bob')
    defaults = {
        'created_by': created_by,
        'phase': kwargs['phase'] if 'phase' in kwargs else create_phase(),
        'category': kwargs['category'] if 'category' in kwargs else create_category(),
        'title': 'My Awesome submission',
        }
    if kwargs:
        defaults.update(kwargs)
    instance, created = Submission.objects.get_or_create(**defaults)
    if with_parent:
        SubmissionParent.objects.get_or_create(submission=instance)
    return instance


def setup_ignite_challenge():
    project = create_project()
    challenge = create_challenge(project=project)
    ideation_phase = create_phase(name=settings.IGNITE_IDEATION_NAME,
                                  challenge=challenge)
    dev_phase = create_phase(name=settings.IGNITE_DEVELOPMENT_NAME,
                             challenge=challenge)
    return {
        'project': project,
        'challenge': challenge,
        'ideation_phase': ideation_phase,
        'dev_phase': dev_phase,
        'round_a': create_phase_round(name='Round A', phase=dev_phase),
        'category': create_category(),
        }


def setup_ideation_phase(is_open=True, **kwargs):
    """Ideation phase is open and Development phase is in the future"""
    now = datetime.utcnow()
    delta = relativedelta(days=10)
    ideation_phase = kwargs['ideation_phase']
    ideation_phase.start_date = (now - delta) if is_open else (now + relativedelta(days=1))
    ideation_phase.end_date = now + delta
    ideation_phase.save()
    dev_phase = kwargs['dev_phase']
    dev_phase.start_date = now + (delta * 2)
    dev_phase.end_date = now + (delta * 3)
    dev_phase.save()
    round_a = kwargs['round_a']
    round_a.start_date = dev_phase.start_date
    round_a.end_date = dev_phase.end_date
    round_a.save()
    kwargs.update({
        'ideation_phase': ideation_phase,
        'dev_phase': dev_phase,
        'round_a': round_a,
        })
    return kwargs


def setup_development_phase(is_round_open=True, **kwargs):
    """Ideation phase is in the past and the Development phase and a Round are
    open"""
    now = datetime.utcnow()
    delta = relativedelta(days=10)
    ideation_phase = kwargs['ideation_phase']
    ideation_phase.start_date = now - (delta * 3)
    ideation_phase.end_date = now - (delta * 2)
    ideation_phase.save()
    dev_phase = kwargs['dev_phase']
    dev_phase.start_date = now - delta
    dev_phase.end_date = now + delta
    dev_phase.save()
    round_a = kwargs['round_a']
    round_a.start_date = dev_phase.start_date
    round_a.end_date = dev_phase.end_date if is_round_open else (now - relativedelta(hours=1))
    round_a.save()
    kwargs.update({
        'ideation_phase': ideation_phase,
        'dev_phase': dev_phase,
        'round_a': round_a,
        })
    return kwargs


def setup_development_rounds_phase(is_round_open=True, **kwargs):
    """Fixtures for seting up a development phase scenario
    - Ideation phase is in the past
    - Development phase is open
    - ``round_b`` is open by default
    """
    now = datetime.utcnow()
    delta = relativedelta(days=10)
    ideation_phase = kwargs['ideation_phase']
    ideation_phase.start_date = now - (delta * 3)
    ideation_phase.end_date = now - (delta * 2)
    ideation_phase.save()
    dev_phase = kwargs['dev_phase']
    dev_phase.start_date = now - delta
    dev_phase.end_date = now + delta
    dev_phase.save()
    round_a = kwargs['round_a']
    round_a.start_date = dev_phase.start_date
    round_a.end_date = now - relativedelta(hours=1)
    round_a.save()
    start_date = now if is_round_open else now + relativedelta(hours=1)
    round_b = create_phase_round(name='Round B', phase=dev_phase,
                                 start_date=start_date,
                                 end_date=dev_phase.end_date)
    kwargs.update({
        'ideation_phase': ideation_phase,
        'dev_phase': dev_phase,
        'round_a': round_a,
        'round_b': round_b,
        })
    return kwargs


def teardown_ignite_challenge():
    for model in [PhaseRound, Phase, Challenge, Project]:
        model.objects.all().delete()
    return
