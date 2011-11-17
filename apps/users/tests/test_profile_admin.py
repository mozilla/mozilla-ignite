from contextlib import contextmanager

import fudge

from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from users.models import Profile, Link


@contextmanager
def given_user(fake_auth, user):
    """Context manager to respond to any login call with a specific user."""
    fake_auth.expects_call().returns(user)
    yield


class ProfileAdmin(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.User = User.objects.create(
            username=u'test_ross',
            password=u'password2',
            is_active=True
        )
        self.profile = Profile.objects.create(
            user=self.User
        )

    @fudge.patch('django_browserid.auth.BrowserIDBackend.authenticate')
    def test_edit_without_links(self, fake):
        redirect = '/profile/%s/' % self.User.username
        post_data = {
            'name': 'Boozeniges',
            'link_url': 'http://ross-eats.co.uk',
            'link_name': 'ross eats'
        }
        
        with given_user(fake, self.User):
            self.client.login()
            response = self.client.post('/profile/edit/', post_data,
                                        follow=True)
        
        try:
            self.assertRedirects(response, redirect, status_code=301)
        except AssertionError:
            print response.redirect_chain
            raise
