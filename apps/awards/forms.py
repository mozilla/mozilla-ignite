from django import forms


class AwardForm(forms.Form):
    amount = forms.IntegerField()
