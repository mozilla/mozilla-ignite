from django.test import Client
from django.contrib.auth.models import User
# This test class gives us access to the Jinja2 template context
from test_utils import TestCase

from ignite.tests.decorators import ignite_skip
from users.models import Profile, Link
from projects.models import Project


class ProfileData(TestCase):

    def setUp(self):
        self.client = Client()
        self.User = User.objects.create_user(
            username=u'testaccount',
            email=u'testaccount@example.com',
            password=u'password1'
        )
        
        # Fill in the minimum of profile details to stop the nagware kicking in
        self.profile = Profile.objects.create(
            user=self.User,
            name='Frank McTestcase'
        )

    @ignite_skip
    def test_social_links(self):
        user_slug = '/en-US/profile/%s/' % self.profile.user.username
        response = self.client.get(user_slug)
        self.assertEqual(response.context['social_links'], False)

        Link.objects.create(
            name=u'Test',
            url=u'http://www.mozilla.org',
            profile=self.profile
        )

        response = self.client.get(user_slug)
        self.assertNotEqual(response.context['social_links'], False)
    
    @ignite_skip
    def test_project_links(self):
        user_slug = '/en-US/profile/%s/' % self.profile.user.username
        response = self.client.get(user_slug)
        self.assertEqual(response.context['projects'], False)

        p = Project.objects.create(
            name=u'Shipment of Fail',
            slug=u'shipment-of-fail',
            description=u'Blah',
            long_description=u'Blah blah'
        )

        p.team_members.add(self.profile)

        response = self.client.get(user_slug)
        self.assertNotEqual(response.context['projects'], False)
