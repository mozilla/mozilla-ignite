from datetime import datetime

from challenges.forms import (EntryForm, NewEntryForm, DevelopmentEntryForm,
                              NewDevelopmentEntryForm)
from challenges.models import Submission, SubmissionParent, ExternalLink
from challenges.tests.fixtures.ignite_fixtures import (setup_ignite_challenge,
                                                       teardown_ignite_challenge,
                                                       setup_ideation_phase,
                                                       setup_development_phase,
                                                       setup_development_rounds_phase,
                                                       create_submission,
                                                       create_user)
from challenges.tests.fixtures import BLANK_EXTERNALS, EXTERNALS
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from test_utils import TestCase

from nose.tools import eq_, ok_


class SubmissionBaseTest(TestCase):

    def setUp(self):
        self.profile = create_user('bob')
        self.ideation_url = reverse('create_entry', args=['ideas'])
        self.development_url = reverse('create_entry', args=['proposals'])

    def _get_valid_data(self, **kwargs):
        defaults = {
            'title': 'This is full of awesomeness',
            'brief_description': 'Short description',
            'description': 'A bit longer description',
            'life_improvements': 'A lot of improvements',
            'is_draft': False,
            'terms_and_conditions': True,
            }
        if kwargs:
            defaults.update(kwargs)
        return defaults

    def tearDown(self):
        teardown_ignite_challenge()
        for model in [SubmissionParent, Submission, User, ExternalLink]:
            model.objects.all().delete()

    def assertRedirectsLogin(self, response):
        login_url = reverse('login')
        eq_(response.status_code, 302)
        ok_(login_url in response['Location'])


# Ideation Phase open

class SubmissionIdeationOpenAnonTest(SubmissionBaseTest):
    """Test an anonymous ``Submission`` with the ``Ideation`` phase open"""

    def setUp(self):
        setup_ideation_phase(**setup_ignite_challenge())
        super(SubmissionIdeationOpenAnonTest, self).setUp()

    def test_ideation_phase_get(self):
        response = self.client.get(self.ideation_url)
        self.assertRedirectsLogin(response)

    def test_ideation_phase_post(self):
        response = self.client.post(self.ideation_url, {})
        self.assertRedirectsLogin(response)


class SubmissionIdeationOpenTest(SubmissionBaseTest):
    """Test a user ``Submission`` on with the ``Ideation`` phase open"""

    def setUp(self):
        super(SubmissionIdeationOpenTest, self).setUp()
        self.initial_data = setup_ideation_phase(**setup_ignite_challenge())
        self.category = self.initial_data['category']
        self.valid_data = self._get_valid_data(category=self.category.id)
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        super(SubmissionIdeationOpenTest, self).tearDown()
        self.client.logout()

    def test_ideation_phase_get(self):
        response = self.client.get(self.ideation_url)
        eq_(response.status_code, 200)
        ok_(isinstance(response.context['form'], NewEntryForm))
        ok_('link_form' in response.context)
        eq_(response.context['error_count'], 0)

    def test_ideation_phase_valid_submission(self):
        """Creates a submission on the ideation phase with the minimum
        data possible"""
        self.valid_data.update(BLANK_EXTERNALS)
        response = self.client.post(self.ideation_url, self.valid_data)
        self.assertRedirects(response, reverse('entries_all', args=['ideas']))
        submission = Submission.objects.get()
        eq_(submission.phase, self.initial_data['ideation_phase'])
        eq_(submission.phase_round, None)
        self.assertFalse(submission.phase_round)
        assert submission.parent, "Parent missing"

    def test_ideation_phase_valid_submission_inline_links(self):
        self.valid_data.update(EXTERNALS)
        response = self.client.post(self.ideation_url, self.valid_data)
        self.assertRedirects(response, reverse('entries_all', args=['ideas']))
        submission = Submission.objects.get()
        link = ExternalLink.objects.get()
        eq_(link.name, 'Mozilla')
        eq_(link.url, 'http://mozilla.org/')
        eq_(link.submission, submission)

    def test_ideation_phase_non_accepted_tnc(self):
        self.valid_data.update(BLANK_EXTERNALS)
        self.valid_data['terms_and_conditions'] = False
        response = self.client.post(self.ideation_url, self.valid_data)
        eq_(response.status_code, 200)
        eq_(Submission.objects.all().count(), 0)


class SubmissionEditIdeationOpenAnonTest(SubmissionBaseTest):
    """Test a anon ``Submission`` edition on with the ``Ideation`` phase open"""

    def setUp(self):
        super(SubmissionEditIdeationOpenAnonTest, self).setUp()
        initial_data = setup_ideation_phase(**setup_ignite_challenge())
        self.submission = create_submission(created_by=self.profile,
                                            phase=initial_data['ideation_phase'])
        self.edit_url = reverse('entry_edit',
                                args=['ideas', self.submission.parent.slug])

    def test_ideation_edit_get(self):
        response = self.client.get(self.edit_url)
        self.assertRedirectsLogin(response)

    def test_ideation_edit_post(self):
        response = self.client.post(self.edit_url, {})
        self.assertRedirectsLogin(response)

    def test_ideation_show_get(self):
        url = reverse('entry_show', args=['ideas', self.submission.parent.slug])
        response = self.client.get(url)
        eq_(response.status_code, 200)
        context = response.context
        eq_(context['entry'], self.submission)
        context_list = ['project', 'challenge', 'links', 'previous',
                        'next', 'user_vote', 'votes', 'excluded',
                        'webcast_list', 'badge_list', 'parent']
        for item in context_list:
            ok_(item in context)

    def test_invalid_url_development_show_get(self):
        url = reverse('entry_show', args=['proposals',
                                          self.submission.parent.slug])
        response = self.client.get(url)
        eq_(response.status_code, 404)


class SubmissionEditIdeationOpenNotOwnerTest(SubmissionBaseTest):
    """Test not an owner ``Submission`` edition on with the ``Ideation``
    phase open"""

    def setUp(self):
        super(SubmissionEditIdeationOpenNotOwnerTest, self).setUp()
        initial_data = setup_ideation_phase(**setup_ignite_challenge())
        other = create_user('other')
        submission = create_submission(created_by=other,
                                       phase=initial_data['ideation_phase'])
        self.edit_url = reverse('entry_edit',
                                args=['ideas', submission.parent.slug])
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        super(SubmissionEditIdeationOpenNotOwnerTest, self).tearDown()
        self.client.logout()

    def test_ideation_edit_get(self):
        response = self.client.get(self.edit_url)
        eq_(response.status_code, 403)

    def test_ideation_edit_post(self):
        response = self.client.post(self.edit_url, {})
        eq_(response.status_code, 403)


class SubmissionEditIdeationOpenTest(SubmissionBaseTest):
    """Test a user ``Submission`` edition on with the ``Ideation`` phase open"""

    def setUp(self):
        super(SubmissionEditIdeationOpenTest, self).setUp()
        initial_data = setup_ideation_phase(**setup_ignite_challenge())
        self.category = initial_data['category']
        self.submission = create_submission(created_by=self.profile,
                                            phase=initial_data['ideation_phase'])
        self.edit_url = reverse('entry_edit',
                                args=['ideas', self.submission.parent.slug])
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        super(SubmissionEditIdeationOpenTest, self).tearDown()
        self.client.logout()

    def test_ideation_edit_get(self):
        response = self.client.get(self.edit_url)
        eq_(response.status_code, 200)
        ok_(isinstance(response.context['form'], EntryForm))

    def test_ideation_edit_post(self):
        valid_data = self._get_valid_data(category=self.category.id,
                                          **BLANK_EXTERNALS)
        del valid_data['terms_and_conditions']
        response = self.client.post(self.edit_url, valid_data, follow=True)
        self.assertRedirects(response, self.submission.get_absolute_url())
        ok_('messages' in response.context)
        for item in list(response.context['messages']):
            eq_(item.tags, 'success')

    def test_invalid_development_url(self):
        url = reverse('entry_edit', args=['proposals', self.submission.parent.slug])
        response = self.client.get(url)
        eq_(response.status_code, 403)


# Ideation Phase closed

class SubmissionIdeationClosedAnonTest(SubmissionBaseTest):
    """Test an anonymous ``Submission`` with the ``Ideation`` phase closed"""

    def setUp(self):
        super(SubmissionIdeationClosedAnonTest, self).setUp()
        setup_ideation_phase(is_open=False, **setup_ignite_challenge())

    def test_development_phase_submission_get(self):
        response = self.client.get(self.ideation_url)
        self.assertRedirectsLogin(response)

    def test_development_phase_submission_post(self):
        response = self.client.post(self.ideation_url, {})
        self.assertRedirectsLogin(response)


class SubmissionIdeationClosedTest(SubmissionBaseTest):
    """Test a user ``Submission`` with the ``Ideation`` phase closed"""

    def setUp(self):
        super(SubmissionIdeationClosedTest, self).setUp()
        self.initial_data = setup_ideation_phase(is_open=False,
                                                 **setup_ignite_challenge())
        self.category = self.initial_data['category']
        self.valid_data = self._get_valid_data(category=self.category.id)
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        super(SubmissionIdeationClosedTest, self).tearDown()
        self.client.logout()

    def test_submission_page_get(self):
        response = self.client.get(self.ideation_url)
        eq_(response.status_code, 403)

    def test_submission_page_post(self):
        self.valid_data.update(BLANK_EXTERNALS)
        response = self.client.post(self.ideation_url, self.valid_data)
        eq_(response.status_code, 403)


class SubmissionEditIdeationClosedAnonTest(SubmissionBaseTest):
    """Test an anon ``Submission`` with the ``Ideation`` phase closed"""

    def setUp(self):
        super(SubmissionEditIdeationClosedAnonTest, self).setUp()
        initial_data = setup_ideation_phase(is_open=False,
                                            **setup_ignite_challenge())
        self.submission = create_submission(created_by=self.profile,
                                            phase=initial_data['ideation_phase'])
        self.edit_url = reverse('entry_edit',
                                args=['ideas', self.submission.parent.slug])

    def test_ideation_edit_get(self):
        response = self.client.get(self.edit_url)
        self.assertRedirectsLogin(response)

    def test_ideation_edit_post(self):
        response = self.client.post(self.edit_url, {})
        self.assertRedirectsLogin(response)

    def test_ideation_show_get(self):
        url = reverse('entry_show', args=['ideas', self.submission.parent.slug])
        response = self.client.get(url)
        eq_(response.status_code, 200)
        context = response.context
        eq_(context['entry'], self.submission)
        context_list = ['project', 'challenge', 'links', 'previous',
                        'next', 'user_vote', 'votes', 'excluded',
                        'webcast_list', 'badge_list', 'parent']
        for item in context_list:
            ok_(item in context)

    def test_invalid_url_development_show_get(self):
        url = reverse('entry_show', args=['proposals',
                                          self.submission.parent.slug])
        response = self.client.get(url)
        eq_(response.status_code, 404)


class SubmissionEditIdeationClosedNotOwnerTest(SubmissionBaseTest):
    """Test not an owner ``Submission`` edition on with the ``Ideation``
    phase closed"""

    def setUp(self):
        super(SubmissionEditIdeationClosedNotOwnerTest, self).setUp()
        initial_data = setup_ideation_phase(is_open=False,
                                            **setup_ignite_challenge())
        other = create_user('other')
        submission = create_submission(created_by=other,
                                       phase=initial_data['ideation_phase'])
        self.edit_url = reverse('entry_edit',
                                args=['ideas', submission.parent.slug])
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        super(SubmissionEditIdeationClosedNotOwnerTest, self).tearDown()
        self.client.logout()

    def test_ideation_edit_get(self):
        response = self.client.get(self.edit_url)
        eq_(response.status_code, 403)

    def test_ideation_edit_post(self):
        response = self.client.post(self.edit_url, {})
        eq_(response.status_code, 403)


class SubmissionEditIdeationClosedTest(SubmissionBaseTest):
    """Test a user ``Submission`` with the ``Ideation`` phase closed"""

    def setUp(self):
        super(SubmissionEditIdeationClosedTest, self).setUp()
        initial_data = setup_ideation_phase(is_open=False,
                                                 **setup_ignite_challenge())
        category = initial_data['category']
        self.valid_data = self._get_valid_data(category=category.id)
        self.submission = create_submission(created_by=self.profile,
                                            phase=initial_data['ideation_phase'])
        self.edit_url = reverse('entry_edit',
                                args=['ideas', self.submission.parent.slug])
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        super(SubmissionEditIdeationClosedTest, self).tearDown()
        self.client.logout()

    def test_ideation_edit_form(self):
        response = self.client.get(self.edit_url)
        eq_(response.status_code, 403)

    def test_ideation_save_edit_failed(self):
        self.valid_data.update(BLANK_EXTERNALS)
        del self.valid_data['terms_and_conditions']
        response = self.client.post(self.edit_url, self.valid_data, follow=True)
        eq_(response.status_code, 403)

    def test_invalid_development_url(self):
        url = reverse('entry_edit',
                      args=['proposals', self.submission.parent.slug])
        response = self.client.get(url)
        eq_(response.status_code, 403)


# Development phase tests

class SubmissionDevelopmentOpenAnonTest(SubmissionBaseTest):
    """Tests anonymous ``Submissions`` when the ``Development`` phase
    is open"""

    def setUp(self):
        super(SubmissionDevelopmentOpenAnonTest, self).setUp()
        setup_development_phase(**setup_ignite_challenge())

    def test_development_phase_submission_get(self):
        response = self.client.get(self.development_url)
        self.assertRedirectsLogin(response)

    def test_development_phase_submission_post(self):
        response = self.client.post(self.development_url, {})
        self.assertRedirectsLogin(response)


class SubmissionDevelopmentOpenTest(SubmissionBaseTest):
    """Tests user ``Submissions`` when the ``Development`` phase
    is open"""

    def setUp(self):
        super(SubmissionDevelopmentOpenTest, self).setUp()
        self.initial_data = setup_development_phase(**setup_ignite_challenge())
        category = self.initial_data['category']
        self.valid_data = self._get_valid_data(category=category.id,
                                               repository_url='http://mozilla.com',
                                               blog_url='http://blog.mozilla.com')
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        super(SubmissionDevelopmentOpenTest, self).tearDown()
        self.client.logout()

    def test_development_phase_get(self):
        response = self.client.get(self.development_url)
        ok_(response.status_code, 200)
        ok_(isinstance(response.context['form'], NewDevelopmentEntryForm))
        ok_('link_form' in response.context)
        eq_(response.context['error_count'], 0)

    def test_development_phase_valid_submission(self):
        """Creates a submission on the development phase with the minimum
        data possible"""
        self.valid_data.update(BLANK_EXTERNALS)
        response = self.client.post(self.development_url, self.valid_data)
        self.assertRedirects(response, reverse('entries_all', args=['proposals']))
        submission = Submission.objects.get()
        eq_(submission.phase, self.initial_data['dev_phase'])
        eq_(submission.phase_round, self.initial_data['round_a'])
        assert submission.parent, "Parent missing"

    def test_development_phase_valid_submission_inline_links(self):
        self.valid_data.update(EXTERNALS)
        response = self.client.post(self.development_url, self.valid_data)
        self.assertRedirects(response, reverse('entries_all', args=['proposals']))
        submission = Submission.objects.get()
        link = ExternalLink.objects.get()
        eq_(link.name, 'Mozilla')
        eq_(link.url, 'http://mozilla.org/')
        eq_(link.submission, submission)

    def test_development_phase_non_accepted_tnc(self):
        self.valid_data.update(BLANK_EXTERNALS)
        self.valid_data['terms_and_conditions'] = False
        response = self.client.post(self.development_url, self.valid_data)
        eq_(response.status_code, 200)
        eq_(Submission.objects.all().count(), 0)


class SubmissionEditDevelopmentOpenAnonTest(SubmissionBaseTest):
    """Test a anon ``Submission`` edition on with the ``Development``
    phase open"""

    def setUp(self):
        super(SubmissionEditDevelopmentOpenAnonTest, self).setUp()
        initial_data = setup_development_rounds_phase(**setup_ignite_challenge())
        self.submission = create_submission(created_by=self.profile,
                                            phase=initial_data['dev_phase'],
                                            phase_round=initial_data['round_b'])
        self.edit_url = reverse('entry_edit',
                                args=['proposals', self.submission.parent.slug])

    def test_development_edit_get(self):
        response = self.client.get(self.edit_url)
        self.assertRedirectsLogin(response)

    def test_development_edit_post(self):
        response = self.client.post(self.edit_url, {})
        self.assertRedirectsLogin(response)

    def test_development_show_get(self):
        url = reverse('entry_show', args=['proposals',
                                          self.submission.parent.slug])
        response = self.client.get(url)
        eq_(response.status_code, 200)
        context = response.context
        eq_(context['entry'], self.submission)
        context_list = ['project', 'challenge', 'links', 'previous',
                        'next', 'user_vote', 'votes', 'excluded',
                        'webcast_list', 'badge_list', 'parent']
        for item in context_list:
            ok_(item in context)

    def test_invalid_url_ideation_show_get(self):
        url = reverse('entry_show', args=['ideas',
                                          self.submission.parent.slug])
        response = self.client.get(url)
        eq_(response.status_code, 404)


class SubmissionEditDevelopmentOpenNotOwnerTest(SubmissionBaseTest):
    """Test a anon ``Submission`` edition on with the ``Development``
    phase open"""

    def setUp(self):
        super(SubmissionEditDevelopmentOpenNotOwnerTest, self).setUp()
        initial_data = setup_development_rounds_phase(**setup_ignite_challenge())
        other = create_user('other')
        submission = create_submission(created_by=other,
                                       phase=initial_data['dev_phase'],
                                       phase_round=initial_data['round_b'])
        self.edit_url = reverse('entry_edit',
                                args=['proposals', submission.parent.slug])
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        super(SubmissionEditDevelopmentOpenNotOwnerTest, self).tearDown()
        self.client.logout()

    def test_development_edit_get(self):
        response = self.client.get(self.edit_url)
        eq_(response.status_code, 403)

    def test_development_edit_post(self):
        response = self.client.post(self.edit_url, {})
        eq_(response.status_code, 403)


class SubmissionEditDevelopmentOpenTest(SubmissionBaseTest):
    """Tests user ``Submissions`` when the ``Development`` phase
    is open"""

    def setUp(self):
        super(SubmissionEditDevelopmentOpenTest, self).setUp()
        self.initial_data = setup_development_rounds_phase(**setup_ignite_challenge())
        category = self.initial_data['category']
        self.valid_data = self._get_valid_data(category=category.id,
                                               repository_url='http://mozilla.com',
                                               blog_url='http://blog.mozilla.com')
        del self.valid_data['terms_and_conditions']
        # Create a proposal ``Submission`` on the open ``PhaseRound``
        self.submission = create_submission(
            created_by=self.profile,
            phase=self.initial_data['dev_phase'],
            phase_round=self.initial_data['round_b'])
        self.edit_url = self._get_edit_url(self.submission.parent.slug)
        self.client.login(username='bob', password='bob')

    def _get_edit_url(self, slug):
        return reverse('entry_edit', args=['proposals', slug])

    def tearDown(self):
        super(SubmissionEditDevelopmentOpenTest, self).tearDown()
        self.client.logout()

    def test_invalid_idea_edit_on_development_get(self):
        idea = create_submission(created_by=self.profile,
                                 phase=self.initial_data['ideation_phase'])
        response = self.client.get(self._get_edit_url(idea.parent.slug))
        eq_(response.status_code, 404)

    def test_invalid_idea_edit_on_development_post(self):
        idea = create_submission(created_by=self.profile,
                                 phase=self.initial_data['ideation_phase'])
        response = self.client.post(self._get_edit_url(idea.parent.slug),
                                    self.valid_data)
        eq_(response.status_code, 404)

    def test_development_edit_form(self):
        response = self.client.get(self.edit_url)
        eq_(response.status_code, 200)
        ok_(isinstance(response.context['form'], DevelopmentEntryForm))

    def test_development_edit_post_same_round(self):
        self.valid_data.update(BLANK_EXTERNALS)
        response = self.client.post(self.edit_url, self.valid_data,
                                    follow=True)
        self.assertRedirects(response, self.submission.get_absolute_url())
        ok_('messages' in response.context)
        for item in list(response.context['messages']):
            eq_(item.tags, 'success')
        parent = SubmissionParent.objects.get()
        ok_(parent.submission, self.submission)
        ok_(parent.slug, str(self.submission.id))
        version_list = parent.submissionversion_set.all()
        eq_(len(version_list), 0)

    def test_development_edit_post_new_round(self):
        SubmissionParent.objects.get().delete()
        submission = create_submission(created_by=self.profile,
                                       phase=self.initial_data['dev_phase'],
                                       phase_round=self.initial_data['round_a'])
        edit_url = self._get_edit_url(submission.parent.slug)
        self.valid_data.update(BLANK_EXTERNALS)
        response = self.client.post(edit_url, self.valid_data)
        self.assertRedirects(response, submission.get_absolute_url())
        parent = SubmissionParent.objects.get()
        version_list = parent.submissionversion_set.all()
        eq_(len(version_list), 1)
        eq_(version_list[0].submission, submission)
        eq_(parent.submission.phase, self.initial_data['dev_phase'])
        eq_(parent.submission.phase_round, self.initial_data['round_b'])

    def test_invalid_ideation_url(self):
        url = reverse('entry_edit', args=['ideas', self.submission.parent.slug])
        response = self.client.get(url)
        eq_(response.status_code, 403)


# Development Phase closed Rounds

class SubmissionDevelopmentClosedRoundAnonTest(SubmissionBaseTest):

    def setUp(self):
        super(SubmissionDevelopmentClosedRoundAnonTest, self).setUp()
        setup_development_phase(is_round_open=False, **setup_ignite_challenge())

    def test_development_phase_submission_get(self):
        response = self.client.get(self.development_url)
        self.assertRedirectsLogin(response)

    def test_development_phase_submission_post(self):
        response = self.client.post(self.development_url, {})
        self.assertRedirectsLogin(response)


class SubmissionDevelopmentClosedRoundTests(SubmissionBaseTest):

    def setUp(self):
        super(SubmissionDevelopmentClosedRoundTests, self).setUp()
        self.initial_data = setup_development_phase(is_round_open=False,
                                                    **setup_ignite_challenge())
        category = self.initial_data['category']
        self.valid_data = self._get_valid_data(category=category.id,
                                               repository_url='http://mozilla.com')
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        super(SubmissionDevelopmentClosedRoundTests, self).tearDown()
        self.client.logout()

    def test_development_phase_submission_page(self):
        response = self.client.get(self.development_url)
        eq_(response.status_code, 403)

    def test_development_phase_submission_post(self):
        self.valid_data.update(BLANK_EXTERNALS)
        response = self.client.post(self.development_url, self.valid_data)
        eq_(response.status_code, 403)


class SubmissionEditDevelopmentClosedRoundAnonTests(SubmissionBaseTest):
    """Test a anon ``Submission`` edition on with the ``Development``
    Phase Round closed"""

    def setUp(self):
        super(SubmissionEditDevelopmentClosedRoundAnonTests, self).setUp()
        initial_data = setup_development_phase(is_round_open=False,
                                               **setup_ignite_challenge())
        self.submission = create_submission(created_by=self.profile,
                                            phase=initial_data['dev_phase'],
                                            phase_round=initial_data['round_a'])
        self.edit_url = reverse('entry_edit',
                                args=['proposals', self.submission.parent.slug])

    def test_development_edit_get(self):
        response = self.client.get(self.edit_url)
        self.assertRedirectsLogin(response)

    def test_development_edit_post(self):
        response = self.client.post(self.edit_url, {})
        self.assertRedirectsLogin(response)

    def test_development_show_get(self):
        url = reverse('entry_show', args=['proposals',
                                          self.submission.parent.slug])
        response = self.client.get(url)
        eq_(response.status_code, 200)
        context = response.context
        eq_(context['entry'], self.submission)
        context_list = ['project', 'challenge', 'links', 'previous',
                        'next', 'user_vote', 'votes', 'excluded',
                        'webcast_list', 'badge_list', 'parent']
        for item in context_list:
            ok_(item in context)

    def test_invalid_url_ideation_show_get(self):
        url = reverse('entry_show', args=['ideas',
                                          self.submission.parent.slug])
        response = self.client.get(url)
        eq_(response.status_code, 404)



class SubmissionEditDevelopmentClosedRoundNotOnwerTests(SubmissionBaseTest):
    """Test a non owner ``Submission`` edition on with the ``Development``
    Phase Round closed"""

    def setUp(self):
        super(SubmissionEditDevelopmentClosedRoundNotOnwerTests, self).setUp()
        initial_data = setup_development_phase(is_round_open=False,
                                               **setup_ignite_challenge())
        other = create_user('other')
        submission = create_submission(created_by=other,
                                       phase=initial_data['dev_phase'],
                                       phase_round=initial_data['round_a'])
        self.edit_url = reverse('entry_edit',
                                args=['proposals', submission.parent.slug])
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        super(SubmissionEditDevelopmentClosedRoundNotOnwerTests, self).tearDown()
        self.client.logout()

    def test_development_edit_get(self):
        response = self.client.get(self.edit_url)
        eq_(response.status_code, 403)

    def test_development_edit_post(self):
        response = self.client.post(self.edit_url, {})
        eq_(response.status_code, 403)


class SubmissionEditDevelopmentClosedRoundTests(SubmissionBaseTest):

    def setUp(self):
        super(SubmissionEditDevelopmentClosedRoundTests, self).setUp()
        initial_data = setup_development_phase(is_round_open=False,
                                               **setup_ignite_challenge())
        category = initial_data['category']
        self.valid_data = self._get_valid_data(category=category.id,
                                               repository_url='http://mozilla.com')
        self.submission = create_submission(created_by=self.profile,
                                            phase=initial_data['dev_phase'],
                                            phase_round=initial_data['round_a'])
        self.edit_url = reverse('entry_edit',
                                args=['proposals', self.submission.parent.slug])
        self.client.login(username='bob', password='bob')

    def tearDown(self):
        super(SubmissionEditDevelopmentClosedRoundTests, self).tearDown()
        self.client.logout()

    def test_development_edit_form(self):
        response = self.client.get(self.edit_url)
        eq_(response.status_code, 403)

    def test_development_save_edit_failure(self):
        self.valid_data.update(BLANK_EXTERNALS)
        del self.valid_data['terms_and_conditions']
        response = self.client.post(self.edit_url, self.valid_data)
        eq_(response.status_code, 403)

    def test_invalid_ideation_url(self):
        url = reverse('entry_edit', args=['ideas', self.submission.parent.slug])
        response = self.client.get(url)
        eq_(response.status_code, 403)
