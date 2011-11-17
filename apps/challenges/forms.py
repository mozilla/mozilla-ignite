from django import forms

from challenges.models import Submission


class EntryForm(forms.ModelForm):
    
    class Meta:
        model = Submission
        fields = (
            'title',
            'brief_description',
            'description',
            'is_draft',
        )
