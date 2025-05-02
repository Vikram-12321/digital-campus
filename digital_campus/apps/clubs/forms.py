from .models import Club, ClubMembership
from django import forms
from django.contrib.auth.models import User
from apps.users.models import Profile

class ClubSignupForm(forms.ModelForm):
    class Meta:
        model  = Club
        fields = ["name", "slug", "description", "banner", "avatar"]
    #
    # save() now puts the creator into **both** owners & members
    #
    def save(self, creator, commit=True):
        club = super().save(commit=False)
        if commit:
            club.save()
            club.owners.add(creator)    # ⇦ here
            club.members.add(creator)
        return club


class ClubMembershipForm(forms.ModelForm):
    class Meta:
        model = ClubMembership
        fields = ['profile', 'club', 'role', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Profile.objects.select_related('user').order_by('user__username')
        self.fields['profile'].queryset = qs
        self.fields['profile'].label_from_instance = lambda prof: prof.user.username
        # you can remove the fixed height if you want a normal dropdown:
        self.fields['profile'].widget.attrs.update({'style': 'width:300px;'})