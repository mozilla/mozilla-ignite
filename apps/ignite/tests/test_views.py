from django.core.urlresolvers import reverse
from django.core.cache import cache
import test_utils

from challenges.models import Submission
from challenges.tests.fixtures import (challenge_setup, challenge_teardown,
                                       create_submissions)
from ignite.tests.decorators import ignite_only


class SplashViewTest(test_utils.TestCase):
    
    def setUp(self):
        challenge_setup()
        cache.clear()
    
    def tearDown(self):
        challenge_teardown()
    
    @ignite_only
    def test_splash_page(self):
        response = self.client.get(reverse('challenge_show'))
        self.assertEqual(response.status_code, 200)
    
    @ignite_only
    def test_splash_page_with_entries(self):
        create_submissions(30)
        response = self.client.get(reverse('challenge_show'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['entries']), 5)
    
    @ignite_only
    def test_splash_draft_entries(self):
        """Test draft entries aren't shown on the splash page."""
        create_submissions(3)
        submissions = Submission.objects.all()
        hidden = submissions[0]
        hidden.is_draft = True
        hidden.save()
        
        response = self.client.get(reverse('challenge_show'))
        self.assertEqual(set(response.context['entries']),
                         set(submissions[1:]))
        
