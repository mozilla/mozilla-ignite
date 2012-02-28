from urlparse import urlsplit

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory
from nose.tools import assert_equal

from ignite.context_processors import browserid_target_processor

class BrowserIDTargetTest(TestCase):
    
    urls = 'django_browserid.urls'
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_root_path(self):
        request = self.factory.get('/')
        context = browserid_target_processor(request)
        assert_equal(context.keys(), ['browserid_target'])
        parts = urlsplit(context['browserid_target'])
        assert_equal(parts.path, reverse('browserid_verify'))
        assert_equal(parts.query, 'next=%2F')
    
    def test_path(self):
        request = self.factory.get('/flibble')
        context = browserid_target_processor(request)
        assert_equal(context.keys(), ['browserid_target'])
        parts = urlsplit(context['browserid_target'])
        assert_equal(parts.path, reverse('browserid_verify'))
        assert_equal(parts.query, 'next=%2Fflibble')
    
    def test_path_with_query(self):
        request = self.factory.get('/flibble?foo=bar&baz=wobble')
        context = browserid_target_processor(request)
        assert_equal(context.keys(), ['browserid_target'])
        parts = urlsplit(context['browserid_target'])
        assert_equal(parts.path, reverse('browserid_verify'))
        assert_equal(parts.query, 'next=%2Fflibble%3Ffoo%3Dbar%26baz%3Dwobble')
    
    def test_double_quoting(self):
        """Test behaviour when the request query has encoded values."""
        request = self.factory.get('/flibble?foo=%2Fflibble%2F')
        context = browserid_target_processor(request)
        assert_equal(context.keys(), ['browserid_target'])
        parts = urlsplit(context['browserid_target'])
        assert_equal(parts.path, reverse('browserid_verify'))
        assert_equal(parts.query, 'next=%2Fflibble%3Ffoo%3D%252Fflibble%252F')
