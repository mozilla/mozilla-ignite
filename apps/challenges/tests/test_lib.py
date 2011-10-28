from django.utils.safestring import SafeString, SafeUnicode
from mock import Mock, patch
from nose.tools import assert_equal

from challenges.lib import cached_render, cached_bleach


@patch('challenges.lib.cache')
def test_cached_render_miss(cache):
    """Check rendering on an empty cache.
    
    The render function should be called, and the result set in the cache
    before returning.
    
    """
    cache.get.return_value = None
    assert_equal(cached_render(str.upper, 'fish', cache_tag='flibble'), 'FISH')
    assert cache.get.called
    assert cache.set.called
    assert_equal(cache.get.call_args[0][0], cache.set.call_args[0][0])
    assert_equal(cache.set.call_args[0][1], 'FISH')


@patch('challenges.lib.cache')
def test_cached_render_hit(cache):
    """Check rendering with a cache hit.
    
    The rendering should be bypassed entirely.
    
    """
    cache.get.return_value = 'I am a cached result'
    dummy_function = Mock()
    result = cached_render(dummy_function, 'fish', cache_tag='flibble')
    assert_equal(result, 'I am a cached result')
    assert isinstance(result, (SafeString, SafeUnicode))
    assert not dummy_function.called
