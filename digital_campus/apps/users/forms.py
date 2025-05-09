from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from dal import autocomplete

from .models import Profile  # Profile is in users/models.py

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered.")
        validate_email(email)
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken.")
        return username


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'image', 
            'bio', 
            'is_private',
            'current_courses',
            'past_courses',
        ]
        widgets = {
            'current_courses': autocomplete.ModelSelect2Multiple(
                url='common:course-autocomplete',
                attrs={
                    'data-placeholder': 'Select current courses...',
                    'data-minimum-input-length': 1,
                }
            ),
            'past_courses': autocomplete.ModelSelect2Multiple(
                url='common:course-autocomplete',
                attrs={
                    'data-placeholder': 'Select past courses...',
                    'data-minimum-input-length': 1,
                }
            ),
        }
