from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import TextInput, EmailInput, PasswordInput
from .models import Profile


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "text",
        'style': 'width: 80%; border-radius:16px; min-height:48px; padding: 8px 16px',
        "placeholder": "Username"
    }))

    email = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "email",
        'style': 'width: 80%; border-radius:16px; min-height:48px; padding: 8px 16px',
        "placeholder": "Email"
    }))

    password1 = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "password",
        'style': 'width: 80%; border-radius:16px; min-height:48px; padding: 8px 16px',
        "placeholder": "Password"
    }))

    password2 = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "password",
        'style': 'width: 80%; border-radius:16px; min-height:48px; padding: 8px 16px',
        "placeholder": "Confirm password"
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "text",
        'style': 'width: 80%; border-radius:16px; min-height:48px; padding: 8px 16px',
        "placeholder": "Username"
    }))

    email = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "email",
        'style': 'width: 80%; border-radius:16px; min-height:48px; padding: 8px 16px',
        "placeholder": "Email"
    }))

    about = forms.CharField(required=False, widget=forms.Textarea(attrs={
        "class": "input",
        "type": "text",
        'style': 'width: 80%; border-radius:16px; min-height:48px; padding: 8px 16px',
        "placeholder": "About Yourself"
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'about']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']
