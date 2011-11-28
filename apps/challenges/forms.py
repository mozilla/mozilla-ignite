from django import forms

from challenges.models import Submission, ExternalLink


class EntryForm(forms.ModelForm):
    
    class Meta:
        model = Submission
        fields = (
            'title',
            'brief_description',
            'description',
            'is_draft',
            'sketh_note',
        )

class EntryLinkForm(forms.ModelForm):

    class Meta:
        model = ExternalLink
        fields = (
            'name',
            'url',
        )
