from datetime import datetime, timedelta

from django.contrib.admin.models import User
from django.conf import settings

from challenges.models import (ExternalLink, Submission, Phase, Challenge,
                               Category, Project)


def challenge_setup():
    """Set up some sample data to test with.
    
    This is a bit clearer and hopefully more flexible than using fixtures.
    
    """
    challenge_teardown()  # In case other tests didn't clean up
    
    p = Project()
    p.name = 'My Project'
    p.slug = getattr(settings, 'IGNITE_PROJECT_SLUG', 'my-project')
    p.description = 'My super awesome project of awesomeness.'
    p.long_description = 'Did I mention how awesome it was?'
    p.allow_participation = True
    p.save()
    
    c = Challenge()
    c.project = p
    c.title, 'My Challenge'
    c.slug = getattr(settings, 'IGNITE_CHALLENGE_SLUG', 'my-challenge')
    c.summary = 'Are you up to it?'
    c.description = 'This is a challenge of supreme challengingness.'
    c.end_date = datetime.now() + timedelta(days=365)
    c.save()
    
    ph = Phase()
    ph.challenge = c
    ph.name = 'Phase 1'
    ph.order = 1
    ph.save()

    cat = Category()
    cat.name = 'Beer'
    cat.slug = 'beer'
    cat.save()


def challenge_teardown():
    """Tear down any data created by these tests."""
    for model in [ExternalLink, Submission, Phase, Challenge, Category, Project, User]:
        model.objects.all().delete()


def create_submissions(count, phase=None, creator=None):
    """Create a number of fake submissions. Return their titles.
    
    If a phase is not supplied, assume only one phase exists.
    
    If a creator is not supplied, try to get a single user's profile, or create
    a dummy user.
    
    """
    if phase is None:
        phase = Phase.objects.get()
    
    if creator is None:
        try:
            user = User.objects.get()
        except User.DoesNotExist:
            user = User.objects.create_user('bob', 'bob@example.com', 'bob')
        creator = user.get_profile()

    category = Category.objects.all()[0]
    
    titles = ['Submission %d' % i for i in range(1, count + 1)]
    for title in titles:
        foo = Submission.objects.create(title=title,
                                  brief_description='A submission',
                                  description='A really good submission',
                                  phase=phase,
                                  created_by=creator,
                                  category=category)
    return titles


def create_users():
    for name in ['alex', 'bob', 'charlie']:
        user = User.objects.create_user(name, '%s@example.com' % name,
                                        password=name)
        # Give the user a display name to stop 'complete your profile' redirect
        profile = user.get_profile()
        profile.name = '%(name)s %(name)sson' % {'name': name.capitalize()}
        profile.save()
