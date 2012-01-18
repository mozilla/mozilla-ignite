from django import forms
from django.forms import widgets
from django.forms.models import inlineformset_factory, ModelChoiceField
from django.forms.util import ErrorDict

from challenges.models import Submission, ExternalLink, Category, \
                              Judgement, JudgingCriterion, JudgingAnswer



class EntryForm(forms.ModelForm):
    
    # Need to specify this explicitly here to remove the empty option
    category = ModelChoiceField(queryset=Category.objects.all(),
                                empty_label=None, widget=forms.RadioSelect())
    class Meta:
        model = Submission
 
        fields = (
            'title',
            'brief_description',
            'description',
            'is_draft',
            'sketh_note',
            'category',
        )
        
        widgets = {
            'title': forms.TextInput(attrs={'aria-describedby':'info_title'}),
            'brief_description': forms.TextInput(attrs={'aria-describedby':'info_brief_description'}),
            'sketh_note': forms.FileInput(attrs={'aria-describedby':'info_sketh_note'}),
            'description': forms.Textarea(attrs={
                'aria-describedby':'info_description',
                'id':'wmd-input',
            }),
            'is_draft': forms.CheckboxInput(attrs={'aria-describedby':'info_is_draft'}),
        }


class AutoDeleteForm(forms.ModelForm):
    """Form class which deletes its instance if all fields are empty."""
    
    def is_blank(self):
        # Using base_fields here to ignore any foreign key or ID fields added
        for name, field in self.base_fields.iteritems():
            field_value = field.widget.value_from_datadict(self.data,
                              self.files, self.add_prefix(name))
            if field_value:
                return False
        
        return True
    
    def full_clean(self):
        if self.is_blank():
            # Blank forms are always valid
            self._errors = ErrorDict()
            self.cleaned_data = {}
            return
        
        super(AutoDeleteForm, self).full_clean()
    
    def save(self, commit=True):
        """Save the contents of this form.
        
        Note that this form will fail if the commit argument is set to False
        and all fields are empty.
        
        """
        if self.is_blank() and self.instance.pk:
            if not commit:
                raise RuntimeError('Auto-deleting forms do not support '
                                   'uncommitted saves.')
            self.instance.delete()
            return None
        
        if self.is_blank() and not self.instance.pk:
            # Nothing to do
            return None
        
        return super(AutoDeleteForm, self).save()


class EntryLinkForm(AutoDeleteForm):

    class Meta:
        model = ExternalLink
        fields = (
            'name',
            'url',
        )


InlineLinkFormSet = inlineformset_factory(Submission, ExternalLink,
                                          can_delete=False, form=EntryLinkForm)


class JudgingForm(forms.ModelForm):
    """A form for judges to rate submissions.
    
    The form is generated dynamically using a list of JudgingCriterion objects,
    each of which is a question about some aspect of the submission. Each of
    these criteria has a numeric range (0 to 10 by default).
    
    """
    
    def __init__(self, *args, **kwargs):
        criteria = kwargs.pop('criteria')
        initial = kwargs.pop('initial', {})
        instance = kwargs.get('instance')
        # Having to do this a bit backwards because we need to retrieve any
        # existing ratings to pass into the superclass constructor, but can't
        # add the extra fields until after the constructor has been called
        new_fields = {}
        for criterion in criteria:
            key = 'criterion_%s' % criterion.pk
            new_fields[key] = self._field_from_criterion(criterion)
            if instance:
                initial[key] = instance.answers.get(criterion=criterion).rating
        
        super(JudgingForm, self).__init__(*args, initial=initial, **kwargs)
        
        self.fields.update(new_fields)
    
    def _field_from_criterion(self, criterion):
        return MinMaxIntegerField(label=criterion.question,
                                  min_value=criterion.min_value,
                                  max_value=criterion.max_value,
                                  widget=RangeInput())
    
    class Meta:
        model = Judgement
        exclude = ('submission', 'judge')


class NumberInput(widgets.Input):
    
    input_type = 'number'


class RangeInput(widgets.Input):
    
    input_type = 'range'


class MinMaxIntegerField(forms.IntegerField):
    """An integer field that supports passing min/max values to its widget."""
    
    widget = NumberInput
    
    def widget_attrs(self, widget):
        return {'min': self.min_value, 'max': self.max_value}
