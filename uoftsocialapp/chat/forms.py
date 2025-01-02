# channels/views.py
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import ChatRoom
from django.contrib.auth.decorators import login_required
from django import forms

class GroupChatForm(forms.Form):
    name = forms.CharField(label="Group Name", max_length=255)
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple
    )
    room_icon = forms.ImageField(required=False)


