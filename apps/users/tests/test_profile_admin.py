import fudge
import logging

from django.test import TestCase, Client
from django.contrib.auth.models import User

from users.models import Profile, Link

log = logging.getLogger(__name__)

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

    @fudge.patch('django_browserid.auth.BrowserIDBackend.authenticate')
    def test_edit_without_links(self, fake):
        redirect = '/profile/%s/' % self.User.username
        log.debug(redirect)
        post_data = {
            'name': 'Boozeniges',
            'link_url': 'http://ross-eats.co.uk',
            'link_name': 'ross eats'
        }
        response = self.client.post('/profile/edit/', post_data, follow=True)
        log.debug(response.redirect_chain)
        self.assertRedirects(response, redirect, status_code=301) 
