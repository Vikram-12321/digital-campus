from .models import Club, ClubMembership
from django import forms
from django.contrib.auth.models import User
from apps.users.models import Profile
from django.core.exceptions import ValidationError

class ClubCreateForm(forms.ModelForm):
    class Meta:
        model  = Club
        fields = ["name", "description", "banner", "avatar"]

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if Club.objects.filter(name__iexact=name).exists():
            raise ValidationError("A club with this name already exists.")
        return name


class ClubMembershipForm(forms.ModelForm):
    class Meta:
        model = ClubMembership
        fields = ['profile', 'club', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Profile.objects.select_related('user').order_by('user__username')
        self.fields['profile'].queryset = qs
        self.fields['profile'].label_from_instance = lambda prof: prof.user.username
        # you can remove the fixed height if you want a normal dropdown:
        self.fields['profile'].widget.attrs.update({'style': 'width:300px;'})