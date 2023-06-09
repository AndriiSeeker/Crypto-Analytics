from cloudinary.forms import CloudinaryFileField
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Profile

user = get_user_model()


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput({'class': 'form-control'}))
    last_name = forms.CharField(max_length=40, required=True, widget=forms.TextInput({'class': 'form-control'}))
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput({'class': 'form-control'}))
    email = forms.CharField(max_length=150, required=True, widget=forms.EmailInput({'class': 'form-control'}))
    password1 = forms.CharField(max_length=20, min_length=5, required=True,
                                widget=forms.PasswordInput({'class': 'form-control'}))
    password2 = forms.CharField(max_length=20, min_length=5, required=True,
                                widget=forms.PasswordInput({'class': 'form-control'}))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput({'class': 'form-control'}))
    password = forms.CharField(max_length=20, min_length=5, required=True,
                               widget=forms.PasswordInput({'class': 'form-control'}))

    class Meta:
        model = User
        fields = ["username", "password"]


class UserForm(RegisterForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]


class ProfileForm(forms.ModelForm):
    bio = forms.CharField(max_length=300, min_length=5, required=False,
                          widget=forms.Textarea({'class': 'form-control', 'rows': 4}), label='bio')

    class Meta:
        model = Profile
        fields = ["avatar", "bio"]


class PasswordChangeForm(forms.ModelForm):
    current_password = forms.CharField(max_length=20, min_length=5, required=True,
                                       widget=forms.PasswordInput({'class': 'form-control'}))
    new_password = forms.CharField(max_length=20, min_length=5, required=True,
                                   widget=forms.PasswordInput({'class': 'form-control'}))

    class Meta:
        model = User
        fields = ["current_password", "new_password"]


class UpdateAvatarFrom(forms.ModelForm):
    image = forms.ImageField()

    class Meta:
        model = Profile
        fields = ["avatar"]

