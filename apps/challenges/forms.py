from django import forms

from tower import ugettext_lazy as _

from challenges.models import Submission


class EntryForm(forms.ModelForm):
    
    class Meta:
        model = Submission
        fields = (
            'title',
            'brief_description',
            'description',
            'created_by'
        )
