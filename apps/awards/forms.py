from django import forms
from django.db.models import Q
from awards.models import Award


class AwardForm(forms.Form):
    amount = forms.IntegerField()


class AwardAdminForm(forms.ModelForm):
    model = Award

    def clean(self):
        if not 'phase' in self.cleaned_data:
            return self.cleaned_data
        args = []
        kwargs = {'phase': self.cleaned_data['phase']}
        if self.cleaned_data.get('phase_round'):
            kwargs.update({'phase_round': self.cleaned_data['phase_round']})
        if self.instance:
            args = [~Q(id=self.instance.id)]
        if self.model.objects.filter(*args, **kwargs):
            raise forms.ValidationError('This Phase/Round combination has '
                                        'already an award')
        return self.cleaned_data
