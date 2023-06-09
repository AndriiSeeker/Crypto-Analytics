from django.forms import ModelForm, ModelChoiceField, Select
from django import forms


# class SearchForm(ModelForm):
#     search_by = ModelChoiceField(queryset=["coin", "news"], required=True, widget=Select())
#
#     class Meta:
#         fields = ['search_by']


class UserDropdownForm(forms.Form):
    OPTIONS = (
        ('profile', 'Profile'),
        ('logout', 'Logout'),
    )
    my_dropdown = forms.ChoiceField(choices=OPTIONS)
