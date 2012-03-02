from django.forms.widgets import RadioSelect, RadioFieldRenderer, RadioInput
from django.forms.util import flatatt
from django.template.defaultfilters import slugify
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


class CustomRadioInput(RadioInput):
    """Mainly duplicated from django.forms.widgets
    Adds extra attributes to the markup"""

    def __unicode__(self):
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = conditional_escape(force_unicode(self.choice_label))
        label_attrs = {'class': slugify(self.choice_label)}
        return mark_safe(u'<label%s %s>%s %s</label>' % (label_for, flatatt(label_attrs),
                                                         self.tag(), choice_label))

    def tag(self):
        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)
        final_attrs = dict(self.attrs, type='radio', name=self.name,
                           value=self.choice_value)
        if self.is_checked():
            final_attrs['checked'] = 'checked'
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class CustomRadioFieldRenderer(RadioFieldRenderer):
    """Mainly duplicated from django.forms.widgets
    Adds extra attributes to the markup"""
    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield CustomRadioInput(self.name, self.value,
                                   self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return CustomRadioInput(self.name, self.value, self.attrs.copy(),
                                choice, idx)

class CustomRadioSelect(RadioSelect):
    """Mainly duplicated from django.forms.widgets
    Adds extra attributes to the markup"""
    renderer = CustomRadioFieldRenderer
