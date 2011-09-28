from django import forms

from tower import ugettext_lazy as _

from participation.models import Entry
from users.models import Profile

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = (
            'title',
            'brief_description',
            'description',
            'created_by'
        )

