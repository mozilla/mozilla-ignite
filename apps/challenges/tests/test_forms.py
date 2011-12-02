from django.test import TestCase
from nose.tools import assert_equal

from challenges.models import ExternalLink
from challenges.forms import EntryLinkForm


class NewLinkFormTest(TestCase):
    
    def setUp(self):
        self.tearDown()
    
    def tearDown(self):
        ExternalLink.objects.all().delete()
    
    def test_new_object(self):
        form = EntryLinkForm(data={'name': 'fish', 'url': 'http://example.com/'})
        assert not form.is_blank()
        assert form.is_valid()
        assert not form.errors
    
        form.save()
        link = ExternalLink.objects.get()
        assert_equal(link.name, 'fish')
        assert_equal(link.url, 'http://example.com/')
    
    def test_blank_new_object(self):
        form = EntryLinkForm(data={})
        assert form.is_blank()
        assert form.is_valid()
        assert not form.errors
        
        form.save()
        assert_equal(ExternalLink.objects.count(), 0)
    
    def test_partial_new_object(self):
        form = EntryLinkForm(data={'name': 'foo', 'url': ''})
        assert not form.is_blank()
        assert not form.is_valid()
        assert form.errors


class ExistingLinkFormTest(TestCase):
    
    def setUp(self):
        self.tearDown()
        ExternalLink.objects.create(name='fish', url='http://example.com/')
    
    def tearDown(self):
        ExternalLink.objects.all().delete()
    
    def test_empty_form(self):
        """Test that an empty form triggers a deletion."""
        form = EntryLinkForm(data={}, instance=ExternalLink.objects.get())
        assert form.is_blank()
        assert form.is_valid()
        assert not form.errors
        
        form.save()
        
        assert_equal(ExternalLink.objects.count(), 0)
    
    def test_partial_form(self):
        form = EntryLinkForm(data={'name': 'blah', 'url': ''},
                             instance=ExternalLink.objects.get())
        
        assert not form.is_blank()
        assert not form.is_valid()
        assert form.errors
