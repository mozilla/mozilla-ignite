from django import forms

from users.models import Profile, Link
from users.widgets import ImageFileInput


class ProfileForm(forms.ModelForm):

    avatar = forms.ImageField(
        widget=ImageFileInput(), required=False)

    class Meta:
        model = Profile
        fields = ('name', 'website', 'avatar', 'bio')
        widgets = {
            'name': forms.TextInput(attrs={'aria-describedby':'name_info'}),
            'website' : forms.TextInput(attrs={'aria-describedby':'website_info'}),
            'bio': forms.Textarea(attrs={'aria-describedby':'bio_info'}),
        }


class ProfileLinksForm(forms.ModelForm):

    class Meta:
        model = Link
        fields = ('name', 'url')
