import os
from functools import wraps

from nose.plugins.skip import SkipTest


def _get_site():
    return os.environ.get('DJANGO_SITE')


def skip_unless(condition):
    """Test decorator to skip a test unless a condition is met.
    
    The condition can either be a callable or a straight value.
    
    """
    
    def decorator(test_fn):
        
        @wraps(test_fn)
        def decorated(*args, **kwargs):
            if not (condition() if callable(condition) else condition):
                raise SkipTest()
            return test_fn(*args, **kwargs)
        
        return decorated
    
    return decorator


ignite_skip = skip_unless(lambda: _get_site() != 'ignite')
ignite_only = skip_unless(lambda: _get_site() == 'ignite')
