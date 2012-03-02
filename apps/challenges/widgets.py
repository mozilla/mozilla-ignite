from django.forms.widgets import RadioSelect, RadioFieldRenderer, RadioInput
from django.forms.util import flatatt
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe


class CustomRadioInput(RadioInput):
    def tag(self):
        if 'id' in self.attrs:
            self.attrs['id'] = '%s_%s' % (self.attrs['id'], self.index)
        final_attrs = dict(self.attrs, type='radio', name=self.name,
                           value=self.choice_value)
        if self.is_checked():
            final_attrs['checked'] = 'checked'
        if not 'class' in self.attrs:
            final_attrs['class'] = slugify(self.choice_label)
        return mark_safe(u'<input%s />' % flatatt(final_attrs))

class CustomRadioFieldRenderer(RadioFieldRenderer):
    def __iter__(self):
        for i, choice in enumerate(self.choices):
            yield CustomRadioInput(self.name, self.value,
                                   self.attrs.copy(), choice, i)

    def __getitem__(self, idx):
        choice = self.choices[idx] # Let the IndexError propogate
        return CustomRadioInput(self.name, self.value, self.attrs.copy(),
                                choice, idx)

class CustomRadioSelect(RadioSelect):
    renderer = CustomRadioFieldRenderer
