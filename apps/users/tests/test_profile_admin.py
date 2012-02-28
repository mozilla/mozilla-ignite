from contextlib import contextmanager

import fudge
import logging

from django.test import TestCase, Client
from django.contrib.auth.models import User

from commons.middleware import LocaleURLMiddleware
from users.models import Profile
from ignite.tests.decorators import ignite_skip

log = logging.getLogger(__name__)

@contextmanager
def given_user(fake_auth, user):
    """Context manager to respond to any login call with a specific user."""
    fake_auth.expects_call().returns(user)
    yield


# Apply this decorator to a test to turn off the middleware that goes around
# inserting 'en_US' redirects into all the URLs
suppress_locale_middleware = fudge.with_patched_object(LocaleURLMiddleware,
                                                       'process_request',
                                                       lambda *args: None)

class ProfileAdmin(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.User = User.objects.create(
            username=u'test_ross',
            password=u'password2',
            email=u'ross@test.com',
            is_active=True
        )
        self.profile = Profile.objects.create(
            user=self.User
        )
    
    @ignite_skip  # To avoid the check that '/' returns a 200
    @suppress_locale_middleware
    @fudge.patch('django_browserid.auth.BrowserIDBackend.authenticate')
    def test_edit_without_links(self, fake):
        redirect = '/'
        post_data = {
            'name': 'Testniges',
            'website': 'http://www.ross-eats.co.uk'
        }

        with given_user(fake, self.User):
            self.client.login()
            response = self.client.post('/profile/edit/', post_data, follow=True)

        self.assertRedirects(response, redirect)
    
    @suppress_locale_middleware
    @fudge.patch('django_browserid.auth.BrowserIDBackend.authenticate')
    def test_edit_with_links(self, fake):
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
        
        self.assertRedirects(response, redirect)
