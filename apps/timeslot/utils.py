import re

from django.db import models
from timeslot.baseconv import base62


default_shortened_models = {
    't': 'timeslot.timeslot',
    }


def shorten_object(obj, shortened_models=None):
    """Shorten a given object"""
    if not shortened_models:
        shortened_models = default_shortened_models
    tiny_id = base62.from_decimal(obj.pk)
    reversed_models = dict((m, p) for p, m in shortened_models.items())
    key = '%s.%s' % (obj._meta.app_label, obj.__class__.__name__.lower())
    if key in reversed_models:
        return u'%s%s' % (reversed_models[key], tiny_id)
    return None


def unshorten_object(shortened, shortened_models=None):
    """Returns the shortened object"""
    if not shortened_models:
        shortened_models = default_shortened_models
    regex = r'^(?P<prefix>%s)(?P<id>\w+)$' % '|'.join(shortened_models.keys())
    match = re.match(regex, shortened)
    if match:
        model = shortened_models[match.group('prefix')]
        try:
            pki = base62.to_decimal(match.group('id'))
        except (AttributeError, ValueError, KeyError):
            return False
        app_label, model_name = model.split('.')
        ModelClass = models.get_model(app_label, model_name)
        try:
            # try to use the ``current`` objects manager when available
            if hasattr(ModelClass, 'current'):
                return ModelClass.current.get(id=pki)
            # fallback to the regular objects manager
            return ModelClass.objects.get(id=pki)
        except ModelClass.DoesNotExist:
            pass
    return False
