# chat/views.py
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import ChatRoom
from django.contrib.auth.decorators import login_required
from django import forms

class GroupChatForm(forms.ModelForm):
    class Meta:
        model  = ChatRoom
        fields = ['name', 'participants', 'room_icon']
        widgets = {
            'participants': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }