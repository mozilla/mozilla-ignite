from functools import partial
from hashlib import md5

import bleach
from django.conf import settings
from django.core.cache import cache
from django.utils.safestring import mark_safe


LONG_CACHE = 60 * 60 * 24 * 7


def cached_render(render_function, source, cache_tag, cache_time=LONG_CACHE):
    """Render a string through a function, using the cache for the result.
    
    The render_function argument should be a single-argument function taking a
    byte or Unicode string and returning a byte or Unicode string.
    
    The cache_tag parameter should be a byte string specific to the rendering
    function, so the cached result can survive restarts but two separate
    functions won't tread on each other's toes.
    
    The result will be returned as a SafeString or SafeUnicode, and so can be
    rendered directly as HTML.
    
    """
    # Make sure the cache key is a byte string, not a Unicode string
    encoded = source.encode('utf8') if isinstance(source, unicode) else source
    cache_key = md5(encoded).hexdigest() + str(cache_tag)
    
    cached = cache.get(cache_key)
    if cached:
        return mark_safe(cached)

    rendered = render_function(source)
    cache.set(cache_key, rendered, cache_time)
    return mark_safe(rendered)


# Generate a bleach cache tag that will be sensitive to changes in settings
_bleach_settings_string = str(settings.TAGS) + str(settings.ALLOWED_ATTRIBUTES)
BLEACH_CACHE_TAG = md5(_bleach_settings_string).hexdigest()


def cached_bleach(source):
    """Render a string through the bleach library, caching the result."""
    render_function = partial(bleach.clean,
                              tags=settings.TAGS,
                              attributes=settings.ALLOWED_ATTRIBUTES)
    return cached_render(render_function, source, cache_tag=BLEACH_CACHE_TAG)


class _Missing(object):

    def __repr__(self):
        return 'no value'

    def __reduce__(self):
        return '_missing'

_missing = _Missing()


class cached_property(object):
    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

        class Foo(object):

            @cached_property
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.

    .. versionchanged:: 0.6
       the `writeable` attribute and parameter was deprecated.  If a
       cached property is writeable or not has to be documented now.
       For performance reasons the implementation does not honor the
       writeable setting and will always make the property writeable.

    :copyright: (c) 2011 by the Werkzeug Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
    """

    # implementation detail: this property is implemented as non-data
    # descriptor.  non-data descriptors are only invoked if there is
    # no entry with the same name in the instance's __dict__.
    # this allows us to completely get rid of the access function call
    # overhead.  If one choses to invoke __get__ by hand the property
    # will still work as expected because the lookup logic is replicated
    # in __get__ for manual invocation.

    def __init__(self, func, name=None, doc=None, writeable=False):
        if writeable:
            from warnings import warn
            warn(DeprecationWarning('the writeable argument to the '
                                    'cached property is a noop since 0.6 '
                                    'because the property is writeable '
                                    'by default for performance reasons'))

        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value
