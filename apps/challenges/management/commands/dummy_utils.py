import random

from challenges.management.commands import identicon
from StringIO import StringIO
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.template.defaultfilters import slugify
from challenges.models import Submission, SubmissionParent


# wording
d = open('/usr/share/dict/words', "r").readlines()
_random_words = lambda n: " ".join([random.choice(d).lower().rstrip() for i in range(n)])
_random_paragraph = lambda: _random_words(30).capitalize()
_random_paragraphs = lambda n: ".\n\n".join([_random_paragraph() for i in range(n)])


def _random_image(name):
    name = "dummy/dummy_%s.png" % name
    icon = identicon.render_identicon(random.randint(5 ** 5, 10 ** 10),
                                      random.randint(64, 250))
    # using storage
    tmp_file = StringIO()
    icon.save(tmp_file, 'PNG')
    return default_storage.save(name, ContentFile(tmp_file.getvalue()))

def create_user(handle):
    """Helper to create Users with a profile"""
    email = '%s@%s.com' % (handle, handle)
    try:
        user = User.objects.get(username=handle)
        return user.get_profile()
    except User.DoesNotExist:
        pass
    user = User.objects.create_user(handle, email, handle)
    profile = user.get_profile()
    # middleware needs a name if not will redirect to edit
    profile.name = handle.title()
    profile.save()
    return profile

def create_submissions(phase, category, phase_round=None, users=50,
                       post_per_user=3, with_parents=False):
    """Creates Random submissions for the given phase, category and round"""
    submission_list = []
    for i in range(users):
        profile = create_user(slugify(_random_words(1)))
        for p in range(post_per_user):
            data = {
                'title': _random_words(4).title(),
                'brief_description': _random_words(15),
                'description': _random_paragraphs(5),
                'category': category,
                'life_improvements': _random_paragraphs(2),
                'interest_making': _random_paragraphs(2),
                'phase': phase,
                'created_by': profile,
                'sketh_note': _random_image(slugify(_random_words(1))),
                }
            if phase_round:
                data['phase_round'] = phase_round
            submission = Submission.objects.create(**data)
            if with_parents:
                SubmissionParent.objects.create(submission=submission)
            submission_list.append(submission)
    return submission_list


def get_random_winners(phase, phase_round=None, total=10):
    params = {'phase': phase}
    if phase_round:
        params['phase_round'] = phase_round
    submissions = Submission.objects.filter(**params).order_by('?')[:total]
    for submission in submissions:
        submission.is_winner = True
        submission.save()
    return submissions
