from django import forms
from django.forms.models import inlineformset_factory, ModelChoiceField
from django.forms.util import ErrorDict

from challenges.models import Submission, ExternalLink, Category


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
