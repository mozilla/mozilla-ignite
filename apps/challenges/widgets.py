from django.forms.widgets import RadioSelect, RadioFieldRenderer, RadioInput
from django.forms.util import flatatt
from django.template.defaultfilters import slugify
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from challenges.models import Category

class CustomRadioFieldRenderer(RadioFieldRenderer):
    """Mainly duplicated from django.forms.widgets
    Adds extra attributes to the markup"""

    def render(self):
        """Outputs a <ul> for this set of radio fields."""
        row_list = []
        # not a generator but more readable
        for w in self:
            # extra attributes
            cat = Category.objects.filter(name=w.choice_label)[0]
            row_attrs = {'class': 'box col %s' % cat.slug}
            row_list.append(u'<li %s>%s</li>' % (flatatt(row_attrs),
                                                 force_unicode(w)))
        return mark_safe(u'<ul>\n%s\n</ul>' % u'\n'.join(row_list))

class CustomRadioSelect(RadioSelect):
    """Mainly duplicated from django.forms.widgets
    Adds extra attributes to the markup"""
    renderer = CustomRadioFieldRenderer
